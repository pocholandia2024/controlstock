"""
Configuración de py2app para generar ControlStock.app en macOS.

Uso:
    pip install -e ".[build-mac]"
    python setup.py py2app
"""

from pathlib import Path

from setuptools import setup

ROOT = Path(__file__).resolve().parent
ICON = ROOT / "assets" / "ControlStock.icns"

APP = ["main.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "iconfile": str(ICON) if ICON.exists() else None,
    "plist": {
        "CFBundleName": "ControlStock",
        "CFBundleDisplayName": "ControlStock",
        "CFBundleIdentifier": "com.controlstock.app",
        "CFBundleVersion": "1.1.0",
        "CFBundleShortVersionString": "1.1.0",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "11.0",
    },
    "packages": ["controlstock"],
    "includes": ["sqlite3", "tkinter"],
}

setup(
    app=APP,
    name="ControlStock",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
