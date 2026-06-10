#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Este script solo funciona en macOS."
  exit 1
fi

echo "==> Creando entorno virtual"
python3 -m venv .venv
source .venv/bin/activate

echo "==> Instalando dependencias"
pip install --upgrade pip
pip install -e ".[build-mac]"

echo "==> Generando icono de la aplicación"
chmod +x scripts/create_icon.sh scripts/create_dmg.sh
./scripts/create_icon.sh

echo "==> Limpiando builds anteriores"
rm -rf build dist
mkdir -p dist

echo "==> Generando ControlStock.app"
python setup.py py2app

echo "==> Creando instalador DMG"
./scripts/create_dmg.sh

echo ""
echo "Listo."
echo "  App : $ROOT_DIR/dist/ControlStock.app"
echo "  DMG : $ROOT_DIR/dist/ControlStock-1.1.0.dmg"
echo ""
echo "Para instalar:"
echo "  open dist/ControlStock-1.1.0.dmg"
