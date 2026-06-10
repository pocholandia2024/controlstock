from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Categoria(str, Enum):
    LAPTOP = "Laptop"
    SMARTPHONE = "Smartphone"
    TABLET = "Tablet"
    ACCESORIO = "Accesorio"
    COMPONENTE = "Componente"
    PERIFERICO = "Periférico"
    AUDIO = "Audio"
    RED = "Red"
    OTRO = "Otro"


class TipoMovimiento(str, Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"


@dataclass
class Producto:
    sku: str
    nombre: str
    categoria: Categoria
    precio: float
    stock: int
    stock_minimo: int = 5
    marca: str = ""
    descripcion: str = ""

    def stock_bajo(self) -> bool:
        return self.stock <= self.stock_minimo

    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "nombre": self.nombre,
            "categoria": self.categoria.value,
            "precio": self.precio,
            "stock": self.stock,
            "stock_minimo": self.stock_minimo,
            "marca": self.marca,
            "descripcion": self.descripcion,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        return cls(
            sku=data["sku"],
            nombre=data["nombre"],
            categoria=Categoria(data["categoria"]),
            precio=float(data["precio"]),
            stock=int(data["stock"]),
            stock_minimo=int(data.get("stock_minimo", 5)),
            marca=data.get("marca", ""),
            descripcion=data.get("descripcion", ""),
        )


@dataclass
class Movimiento:
    sku: str
    tipo: TipoMovimiento
    cantidad: int
    motivo: str
    fecha: str = field(default_factory=ahora_iso)
    stock_resultante: Optional[int] = None
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "tipo": self.tipo.value,
            "cantidad": self.cantidad,
            "motivo": self.motivo,
            "fecha": self.fecha,
            "stock_resultante": self.stock_resultante,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Movimiento":
        return cls(
            sku=data["sku"],
            tipo=TipoMovimiento(data["tipo"]),
            cantidad=int(data["cantidad"]),
            motivo=data["motivo"],
            fecha=data["fecha"],
            stock_resultante=data.get("stock_resultante"),
        )
