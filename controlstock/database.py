"""Capa de persistencia SQLite para ControlStock."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from controlstock.models import Categoria, Movimiento, Producto, TipoMovimiento, ahora_iso
from controlstock.paths import ruta_base_de_datos, ruta_json_legacy

SCHEMA = """
CREATE TABLE IF NOT EXISTS productos (
    sku TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL CHECK (precio >= 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    stock_minimo INTEGER NOT NULL DEFAULT 5 CHECK (stock_minimo >= 0),
    marca TEXT NOT NULL DEFAULT '',
    descripcion TEXT NOT NULL DEFAULT '',
    creado_en TEXT NOT NULL,
    actualizado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL REFERENCES productos(sku) ON DELETE CASCADE,
    tipo TEXT NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    motivo TEXT NOT NULL,
    fecha TEXT NOT NULL,
    stock_resultante INTEGER
);

CREATE INDEX IF NOT EXISTS idx_movimientos_sku ON movimientos(sku);
CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos(fecha DESC);
"""


class BaseDeDatos:
    def __init__(self, ruta: Path | None = None, migrar_json: bool = True) -> None:
        self.ruta = ruta or ruta_base_de_datos()
        self._es_ruta_predeterminada = ruta is None
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar()
        if migrar_json and self._es_ruta_predeterminada:
            self._migrar_desde_json_si_corresponde()

    @contextmanager
    def conexion(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.ruta)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _inicializar(self) -> None:
        with self.conexion() as conn:
            conn.executescript(SCHEMA)

    def _migrar_desde_json_si_corresponde(self) -> None:
        ruta_json = ruta_json_legacy()
        if not ruta_json.exists():
            return

        with self.conexion() as conn:
            total = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
            if total > 0:
                return

            with ruta_json.open(encoding="utf-8") as archivo:
                datos = json.load(archivo)

            for sku, prod in datos.get("productos", {}).items():
                producto = Producto.from_dict(prod)
                ahora = ahora_iso()
                conn.execute(
                    """
                    INSERT INTO productos (
                        sku, nombre, categoria, precio, stock, stock_minimo,
                        marca, descripcion, creado_en, actualizado_en
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        producto.sku,
                        producto.nombre,
                        producto.categoria.value,
                        producto.precio,
                        producto.stock,
                        producto.stock_minimo,
                        producto.marca,
                        producto.descripcion,
                        ahora,
                        ahora,
                    ),
                )

            skus_migrados = set(datos.get("productos", {}).keys())
            for mov_data in datos.get("movimientos", []):
                movimiento = Movimiento.from_dict(mov_data)
                if movimiento.sku not in skus_migrados:
                    continue
                conn.execute(
                    """
                    INSERT INTO movimientos (sku, tipo, cantidad, motivo, fecha, stock_resultante)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        movimiento.sku,
                        movimiento.tipo.value,
                        movimiento.cantidad,
                        movimiento.motivo,
                        movimiento.fecha,
                        movimiento.stock_resultante,
                    ),
                )

        respaldo = ruta_json.with_suffix(".json.bak")
        ruta_json.rename(respaldo)

    def _fila_a_producto(self, fila: sqlite3.Row) -> Producto:
        return Producto(
            sku=fila["sku"],
            nombre=fila["nombre"],
            categoria=Categoria(fila["categoria"]),
            precio=float(fila["precio"]),
            stock=int(fila["stock"]),
            stock_minimo=int(fila["stock_minimo"]),
            marca=fila["marca"],
            descripcion=fila["descripcion"],
        )

    def _fila_a_movimiento(self, fila: sqlite3.Row) -> Movimiento:
        return Movimiento(
            id=fila["id"],
            sku=fila["sku"],
            tipo=TipoMovimiento(fila["tipo"]),
            cantidad=int(fila["cantidad"]),
            motivo=fila["motivo"],
            fecha=fila["fecha"],
            stock_resultante=fila["stock_resultante"],
        )

    def existe_producto(self, sku: str) -> bool:
        with self.conexion() as conn:
            fila = conn.execute(
                "SELECT 1 FROM productos WHERE sku = ?", (sku,)
            ).fetchone()
            return fila is not None

    def obtener_producto(self, sku: str) -> Producto | None:
        with self.conexion() as conn:
            fila = conn.execute(
                "SELECT * FROM productos WHERE sku = ?", (sku,)
            ).fetchone()
            return self._fila_a_producto(fila) if fila else None

    def insertar_producto(self, producto: Producto, fecha: str) -> None:
        with self.conexion() as conn:
            conn.execute(
                """
                INSERT INTO productos (
                    sku, nombre, categoria, precio, stock, stock_minimo,
                    marca, descripcion, creado_en, actualizado_en
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    producto.sku,
                    producto.nombre,
                    producto.categoria.value,
                    producto.precio,
                    producto.stock,
                    producto.stock_minimo,
                    producto.marca,
                    producto.descripcion,
                    fecha,
                    fecha,
                ),
            )

    def actualizar_stock(self, sku: str, stock: int, fecha: str) -> None:
        with self.conexion() as conn:
            conn.execute(
                "UPDATE productos SET stock = ?, actualizado_en = ? WHERE sku = ?",
                (stock, fecha, sku),
            )

    def eliminar_producto(self, sku: str) -> None:
        with self.conexion() as conn:
            conn.execute("DELETE FROM productos WHERE sku = ?", (sku,))

    def listar_productos(
        self, categoria: Categoria | None = None, solo_stock_bajo: bool = False
    ) -> list[Producto]:
        consulta = "SELECT * FROM productos"
        condiciones: list[str] = []
        params: list = []

        if categoria:
            condiciones.append("categoria = ?")
            params.append(categoria.value)
        if solo_stock_bajo:
            condiciones.append("stock <= stock_minimo")

        if condiciones:
            consulta += " WHERE " + " AND ".join(condiciones)
        consulta += " ORDER BY nombre COLLATE NOCASE"

        with self.conexion() as conn:
            filas = conn.execute(consulta, params).fetchall()
            return [self._fila_a_producto(fila) for fila in filas]

    def buscar_productos(self, termino: str) -> list[Producto]:
        patron = f"%{termino}%"
        with self.conexion() as conn:
            filas = conn.execute(
                """
                SELECT * FROM productos
                WHERE sku LIKE ? COLLATE NOCASE
                   OR nombre LIKE ? COLLATE NOCASE
                   OR marca LIKE ? COLLATE NOCASE
                   OR categoria LIKE ? COLLATE NOCASE
                ORDER BY nombre COLLATE NOCASE
                """,
                (patron, patron, patron, patron),
            ).fetchall()
            return [self._fila_a_producto(fila) for fila in filas]

    def insertar_movimiento(self, movimiento: Movimiento) -> Movimiento:
        with self.conexion() as conn:
            cursor = conn.execute(
                """
                INSERT INTO movimientos (sku, tipo, cantidad, motivo, fecha, stock_resultante)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    movimiento.sku,
                    movimiento.tipo.value,
                    movimiento.cantidad,
                    movimiento.motivo,
                    movimiento.fecha,
                    movimiento.stock_resultante,
                ),
            )
            movimiento.id = cursor.lastrowid
            return movimiento

    def listar_movimientos(self, sku: str | None = None, limite: int = 20) -> list[Movimiento]:
        with self.conexion() as conn:
            if sku:
                filas = conn.execute(
                    """
                    SELECT * FROM movimientos
                    WHERE sku = ?
                    ORDER BY fecha DESC, id DESC
                    LIMIT ?
                    """,
                    (sku, limite),
                ).fetchall()
            else:
                filas = conn.execute(
                    """
                    SELECT * FROM movimientos
                    ORDER BY fecha DESC, id DESC
                    LIMIT ?
                    """,
                    (limite,),
                ).fetchall()
            return [self._fila_a_movimiento(fila) for fila in filas]

    def resumen(self) -> dict:
        with self.conexion() as conn:
            fila = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_productos,
                    COALESCE(SUM(stock), 0) AS unidades_en_stock,
                    COALESCE(SUM(precio * stock), 0) AS valor_inventario,
                    COALESCE(SUM(CASE WHEN stock <= stock_minimo THEN 1 ELSE 0 END), 0)
                        AS productos_stock_bajo
                FROM productos
                """
            ).fetchone()
            return {
                "total_productos": int(fila["total_productos"]),
                "unidades_en_stock": int(fila["unidades_en_stock"]),
                "valor_inventario": float(fila["valor_inventario"]),
                "productos_stock_bajo": int(fila["productos_stock_bajo"]),
            }
