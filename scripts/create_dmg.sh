#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

APP_NAME="ControlStock"
VERSION="1.1.0"
APP_PATH="dist/${APP_NAME}.app"
STAGING="build/dmg_staging"
DMG_PATH="dist/${APP_NAME}-${VERSION}.dmg"

if [[ ! -d "$APP_PATH" ]]; then
  echo "No se encontró $APP_PATH"
  echo "Ejecuta primero: ./scripts/build_mac.sh"
  exit 1
fi

echo "==> Preparando imagen DMG"
rm -rf "$STAGING" "$DMG_PATH"
mkdir -p "$STAGING"

cp -R "$APP_PATH" "$STAGING/"
ln -s /Applications "$STAGING/Applications"

echo "==> Creando $DMG_PATH"
hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$STAGING" \
  -ov \
  -format UDZO \
  "$DMG_PATH" >/dev/null

rm -rf "$STAGING"

echo ""
echo "DMG listo:"
echo "  $ROOT_DIR/$DMG_PATH"
echo ""
echo "Para abrirlo:"
echo "  open \"$DMG_PATH\""
