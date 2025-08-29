#!/bin/bash
echo "Building SmartCompute for Android..."
echo

# Install Buildozer requirements
pip3 install -r requirements-mobile.txt

# Initialize buildozer (first time only)
if [ ! -f "buildozer.spec" ]; then
    buildozer init
fi

# Build Android APK
buildozer android debug

echo
echo "Android build completed!"
echo "APK: bin/smartcompute-*-armeabi-v7a-debug.apk"
