#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SOURCE="${1:-assets/icon_source.png}"
SQUARE="assets/icon_square.png"
ICONSET="assets/ControlStock.iconset"
OUTPUT="assets/ControlStock.icns"

if [[ ! -f "$SOURCE" ]]; then
  echo "No se encontró la imagen fuente: $SOURCE"
  exit 1
fi

echo "==> Preparando imagen cuadrada"
ANCHO=$(sips -g pixelWidth "$SOURCE" | awk '/pixelWidth/ {print $2}')
ALTO=$(sips -g pixelHeight "$SOURCE" | awk '/pixelHeight/ {print $2}')
LADO=$(( ANCHO < ALTO ? ANCHO : ALTO ))
sips -c "$LADO" "$LADO" "$SOURCE" --out "$SQUARE" >/dev/null

echo "==> Generando icono macOS"
rm -rf "$ICONSET"
mkdir -p "$ICONSET"

sips -z 16 16     "$SQUARE" --out "$ICONSET/icon_16x16.png"      >/dev/null
sips -z 32 32     "$SQUARE" --out "$ICONSET/icon_16x16@2x.png"   >/dev/null
sips -z 32 32     "$SQUARE" --out "$ICONSET/icon_32x32.png"      >/dev/null
sips -z 64 64     "$SQUARE" --out "$ICONSET/icon_32x32@2x.png"   >/dev/null
sips -z 128 128   "$SQUARE" --out "$ICONSET/icon_128x128.png"    >/dev/null
sips -z 256 256   "$SQUARE" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
sips -z 256 256   "$SQUARE" --out "$ICONSET/icon_256x256.png"    >/dev/null
sips -z 512 512   "$SQUARE" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
sips -z 512 512   "$SQUARE" --out "$ICONSET/icon_512x512.png"    >/dev/null
sips -z 1024 1024 "$SQUARE" --out "$ICONSET/icon_512x512@2x.png" >/dev/null

iconutil -c icns "$ICONSET" -o "$OUTPUT"
rm -rf "$ICONSET"

echo "Icono creado: $OUTPUT"
