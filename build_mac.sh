#!/bin/bash

echo "========================================================"
echo " X Auto Poster - Mac Build Script"
echo "========================================================"

# 1. Environment Setup
echo "[1/5] Setting up Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 2. Browser Download
echo "[2/5] Downloading Browsers..."
# Download to a temporary location first
mkdir -p dist/browsers
export PLAYWRIGHT_BROWSERS_PATH=$(pwd)/dist/browsers
playwright install chromium firefox

# 3. Build Application
echo "[3/5] Building .app with PyInstaller..."
# Clean previous build
rm -rf build dist/X_Auto_Poster.app

pyinstaller --noconfirm --onefile --windowed --name "X_Auto_Poster" \
 --add-data "settings.json:." \
 --add-data "personas.json:." \
 --add-data "accounts.csv:." \
 --hidden-import=customtkinter \
 --hidden-import=google.generativeai \
 main.py

# 4. Bundle Browsers into .app
echo "[4/5] Bundling Browsers into .app..."
# Copy browsers to Contents/MacOS where the executable lives
cp -r dist/browsers dist/X_Auto_Poster.app/Contents/MacOS/

# 5. Create Distribution Zip
echo "[5/5] Creating Distribution Zip..."
PACKAGE_DIR="Output_Mac_v1.8.2"
ZIP_FILE="X_Auto_Poster_Mac_v1.8.2.zip"

rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy App
cp -r dist/X_Auto_Poster.app "$PACKAGE_DIR/"

# Copy Docs
cp "X_Auto_Poster_Win_Source/最初に読んで下さい.txt" "$PACKAGE_DIR/"
cp manual.html "$PACKAGE_DIR/"

# Zip it
zip -r "$ZIP_FILE" "$PACKAGE_DIR"

echo "========================================================"
echo " SUCCESS! Mac Build Complete."
echo " Zip File: $ZIP_FILE"
echo "========================================================"
