@echo off
echo Building Risky Biscy executable...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    pause
    exit /b 1
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Build executable with PyInstaller
echo Building executable...
pyinstaller --onefile --windowed --name "RiskyBiscy" --icon=icon.ico risky_biscy.py

REM Check if build was successful
if exist "dist\RiskyBiscy.exe" (
    echo.
    echo ===================================
    echo BUILD SUCCESSFUL!
    echo ===================================
    echo Executable created: dist\RiskyBiscy.exe
    echo.
    echo You can now distribute this .exe file!
) else (
    echo.
    echo BUILD FAILED!
    echo Check the output above for errors.
)

pause
