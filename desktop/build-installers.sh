#!/bin/bash
# SPYME — One-shot laptop installer builder (macOS + Linux)
# Outputs: dist/SPYME.dmg (macOS) + dist/SPYME-Setup.exe (Windows cross-build)

set -e
cd "$(dirname "$0")"

echo "========================================"
echo "SPYME Laptop Installer Builder"
echo "========================================"

echo
echo "[1/3] Installing dependencies..."
npm install

echo
echo "[2/3] Building installers..."
if [[ "$OSTYPE" == "darwin"* ]]; then
  npx electron-builder --mac --x64 --publish never
  npx electron-builder --win --x64 --publish never
else
  npx electron-builder --win --x64 --publish never
fi

echo
echo "[3/3] Done."
ls -lh dist/
echo
echo "Upload artifacts to GitHub Releases for free distribution."
