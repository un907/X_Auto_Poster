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

# 2. Build with PyInstaller
echo "[2/4] Building .app with PyInstaller..."
# Clean previous build
rm -rf build dist/X_Auto_Poster.app

# ブラウザは同梱しないため、--add-data オプションは削除
pyinstaller --noconfirm --onefile --windowed --name "X_Auto_Poster" \
    --icon="icon-windowed.icns" \
    --add-data "settings.json:." \
    --add-data "accounts.csv:." \
    --add-data "personas.json:." \
    --add-data "images:images" \
    --hidden-import=customtkinter \
    --hidden-import=google.generativeai \
    main.py

# 3. Create Distribution Zip
echo "[3/4] Creating Distribution Zip..."
PACKAGE_DIR="Output_Mac_v1.9.0"
ZIP_FILE="X_Auto_Poster_Mac_v1.9.0.zip"

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
