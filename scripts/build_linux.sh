#!/bin/bash
echo "Building SmartCompute for Linux..."
echo

# Install requirements
pip3 install -r requirements-desktop.txt

# Create executable with PyInstaller
pyinstaller \
    --onefile \
    --windowed \
    --name "smartcompute" \
    --icon "assets/cat_icon.png" \
    --add-data "app:app" \
    --add-data "assets:assets" \
    --distpath "dist/linux" \
    desktop/smartcompute_gui.py

echo
echo "Linux build completed!"
echo "Executable: dist/linux/smartcompute"
