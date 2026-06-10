# ControlStock

Sistema de control de inventario en Python para una **tienda de tecnología**. Incluye interfaz gráfica para macOS, base de datos SQLite propia y empaquetado como aplicación instalable (`.app`).

## Requisitos

- Python 3.10 o superior (macOS 11+)
- Sin dependencias en tiempo de ejecución (solo biblioteca estándar)

## Uso en desarrollo

```bash
cd controlstock
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Interfaz gráfica (por defecto)
python main.py

# Versión de consola
python main.py --cli
```

## Instalar en macOS (.app y .dmg)

Genera la aplicación con icono personalizado y un instalador `.dmg`:

```bash
chmod +x scripts/build_mac.sh
./scripts/build_mac.sh
```

Archivos generados:

```text
dist/ControlStock.app          # aplicación
dist/ControlStock-1.1.0.dmg  # instalador para distribuir
```

Abre el DMG y arrastra **ControlStock** a **Aplicaciones**:

```bash
open dist/ControlStock-1.1.0.dmg
```

Scripts individuales (opcional):

```bash
./scripts/create_icon.sh   # regenera assets/ControlStock.icns
./scripts/create_dmg.sh    # empaqueta dist/ControlStock.app en DMG
```

También puedes instalarla con pip en el sistema:

```bash
pip install -e .
controlstock          # abre la interfaz gráfica
controlstock-cli      # abre la consola
```

## Base de datos

Los datos se guardan en **SQLite**:

| Entorno | Ubicación |
|---------|-----------|
| Desarrollo | `data/inventario.db` en el proyecto |
| App instalada | `~/Library/Application Support/ControlStock/inventario.db` |

Si tenías datos en el formato JSON anterior (`data/inventario.json`), se migran automáticamente la primera vez que abres la app con SQLite. El JSON original se renombra a `inventario.json.bak`.

## Funcionalidades

- Resumen del inventario (productos, unidades, valor total, alertas)
- Catálogo de productos con búsqueda
- Entradas, salidas y ajustes de stock
- Historial de movimientos
- Alertas de stock bajo
- Categorías: Laptop, Smartphone, Tablet, Accesorio, Componente, Periférico, Audio, Red, Otro

## Estructura del proyecto

```text
controlstock/
├── main.py
├── pyproject.toml
├── setup.py              # empaquetado py2app
├── scripts/build_mac.sh
├── controlstock/
│   ├── models.py
│   ├── paths.py          # rutas según entorno
│   ├── database.py       # SQLite
│   ├── inventory.py
│   ├── gui.py            # interfaz gráfica
│   └── cli.py            # consola
└── data/
    └── inventario.db     # base de datos (desarrollo)
```

## Notas para macOS

- La app usa **tkinter**, incluido en Python oficial de [python.org](https://www.python.org/downloads/macos/).
- Si usas Python de Homebrew, instala tkinter con: `brew install python-tk@3.12` (ajusta la versión).
- Para distribuir la app a otras Mac sin Python instalado, comparte `dist/ControlStock-1.1.0.dmg`.
- El icono fuente está en `assets/icon_source.png`; puedes reemplazarlo y ejecutar `./scripts/create_icon.sh`.
