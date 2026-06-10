from controlstock.database import BaseDeDatos
from controlstock.models import Categoria, Movimiento, Producto, TipoMovimiento, ahora_iso


class ErrorInventario(Exception):
    pass


class Inventario:
    def __init__(self, base_de_datos: BaseDeDatos | None = None) -> None:
        self.db = base_de_datos or BaseDeDatos()

    def agregar_producto(
        self,
        sku: str,
        nombre: str,
        categoria: Categoria,
        precio: float,
        stock: int,
        stock_minimo: int = 5,
        marca: str = "",
        descripcion: str = "",
    ) -> Producto:
        sku = sku.strip().upper()
        if not sku:
            raise ErrorInventario("El SKU no puede estar vacío.")
        if self.db.existe_producto(sku):
            raise ErrorInventario(f"Ya existe un producto con SKU '{sku}'.")
        if precio < 0:
            raise ErrorInventario("El precio no puede ser negativo.")
        if stock < 0:
            raise ErrorInventario("El stock inicial no puede ser negativo.")
        if stock_minimo < 0:
            raise ErrorInventario("El stock mínimo no puede ser negativo.")

        producto = Producto(
            sku=sku,
            nombre=nombre.strip(),
            categoria=categoria,
            precio=precio,
            stock=stock,
            stock_minimo=stock_minimo,
            marca=marca.strip(),
            descripcion=descripcion.strip(),
        )
        self.db.insertar_producto(producto, ahora_iso())

        if stock > 0:
            self._registrar_movimiento(
                sku,
                TipoMovimiento.ENTRADA,
                stock,
                "Stock inicial",
            )

        return producto

    def obtener_producto(self, sku: str) -> Producto:
        sku = sku.strip().upper()
        producto = self.db.obtener_producto(sku)
        if producto is None:
            raise ErrorInventario(f"No se encontró el producto con SKU '{sku}'.")
        return producto

    def listar_productos(
        self, categoria: Categoria | None = None, solo_stock_bajo: bool = False
    ) -> list[Producto]:
        return self.db.listar_productos(categoria, solo_stock_bajo)

    def buscar(self, termino: str) -> list[Producto]:
        termino = termino.strip().lower()
        if not termino:
            return []
        return self.db.buscar_productos(termino)

    def _registrar_movimiento(
        self,
        sku: str,
        tipo: TipoMovimiento,
        cantidad: int,
        motivo: str,
    ) -> Movimiento:
        producto = self.obtener_producto(sku)
        movimiento = Movimiento(
            sku=sku,
            tipo=tipo,
            cantidad=cantidad,
            motivo=motivo,
            stock_resultante=producto.stock,
        )
        return self.db.insertar_movimiento(movimiento)

    def entrada_stock(self, sku: str, cantidad: int, motivo: str = "Reposición") -> Producto:
        if cantidad <= 0:
            raise ErrorInventario("La cantidad de entrada debe ser mayor a cero.")

        producto = self.obtener_producto(sku)
        producto.stock += cantidad
        self.db.actualizar_stock(producto.sku, producto.stock, ahora_iso())
        self._registrar_movimiento(sku, TipoMovimiento.ENTRADA, cantidad, motivo)
        return producto

    def salida_stock(self, sku: str, cantidad: int, motivo: str = "Venta") -> Producto:
        if cantidad <= 0:
            raise ErrorInventario("La cantidad de salida debe ser mayor a cero.")

        producto = self.obtener_producto(sku)
        if producto.stock < cantidad:
            raise ErrorInventario(
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Disponible: {producto.stock}, solicitado: {cantidad}."
            )

        producto.stock -= cantidad
        self.db.actualizar_stock(producto.sku, producto.stock, ahora_iso())
        self._registrar_movimiento(sku, TipoMovimiento.SALIDA, cantidad, motivo)
        return producto

    def ajustar_stock(self, sku: str, nuevo_stock: int, motivo: str) -> Producto:
        if nuevo_stock < 0:
            raise ErrorInventario("El stock no puede ser negativo.")
        if not motivo.strip():
            raise ErrorInventario("Debes indicar un motivo para el ajuste.")

        producto = self.obtener_producto(sku)
        diferencia = nuevo_stock - producto.stock
        if diferencia == 0:
            return producto

        producto.stock = nuevo_stock
        self.db.actualizar_stock(producto.sku, producto.stock, ahora_iso())
        self._registrar_movimiento(
            sku,
            TipoMovimiento.AJUSTE,
            abs(diferencia),
            f"{motivo} (ajuste a {nuevo_stock})",
        )
        return producto

    def eliminar_producto(self, sku: str) -> None:
        sku = sku.strip().upper()
        if not self.db.existe_producto(sku):
            raise ErrorInventario(f"No se encontró el producto con SKU '{sku}'.")
        self.db.eliminar_producto(sku)

    def historial_movimientos(self, sku: str | None = None, limite: int = 20) -> list[Movimiento]:
        if sku:
            sku = sku.strip().upper()
        return self.db.listar_movimientos(sku, limite)

    def resumen(self) -> dict:
        return self.db.resumen()

    @property
    def ruta_base_de_datos(self) -> str:
        return str(self.db.ruta)
