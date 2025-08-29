#!/bin/bash
echo "Building SmartCompute for macOS..."
echo

# Install requirements
pip3 install -r requirements-desktop.txt

# Create app bundle with PyInstaller
pyinstaller \
    --onefile \
    --windowed \
    --name "SmartCompute" \
    --icon "assets/icon.icns" \
    --add-data "app:app" \
    --add-data "assets:assets" \
    --distpath "dist/macos" \
    desktop/smartcompute_gui.py

echo
echo "macOS build completed!"
echo "App bundle: dist/macos/SmartCompute.app"
