@echo off
echo Building SmartCompute for Windows...
echo.

REM Install requirements
pip install -r requirements-desktop.txt

REM Create executable with PyInstaller
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "SmartCompute" ^
    --icon "assets\icon.ico" ^
    --add-data "app;app" ^
    --add-data "assets;assets" ^
    --distpath "dist\windows" ^
    desktop\smartcompute_gui.py

echo.
echo Windows build completed!
echo Executable: dist\windows\SmartCompute.exe
pause
