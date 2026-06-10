"""Rutas de datos según el entorno (desarrollo o app instalada en macOS)."""

from __future__ import annotations

import sys
from pathlib import Path

APP_NAME = "ControlStock"


def es_app_empaquetada() -> bool:
    return getattr(sys, "frozen", False)


def directorio_datos() -> Path:
    """Directorio persistente de la aplicación."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        base = Path.home() / ".local" / "share" / APP_NAME

    base.mkdir(parents=True, exist_ok=True)
    return base


def ruta_base_de_datos() -> Path:
    """Ruta del archivo SQLite."""
    if es_app_empaquetada():
        return directorio_datos() / "inventario.db"

    ruta_desarrollo = Path(__file__).resolve().parent.parent / "data" / "inventario.db"
    ruta_desarrollo.parent.mkdir(parents=True, exist_ok=True)
    return ruta_desarrollo


def ruta_json_legacy() -> Path:
    """Ruta del inventario JSON anterior (solo migración)."""
    if es_app_empaquetada():
        return directorio_datos() / "inventario.json"

    return Path(__file__).resolve().parent.parent / "data" / "inventario.json"
