@echo off
setlocal

cd /d "%~dp0"

echo Installing/updating PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    pause
    exit /b 1
)

echo Building card_game.exe...
python -m PyInstaller --clean --noconfirm --onefile --name card_game run_game.py
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete: dist\card_game.exe
pause
