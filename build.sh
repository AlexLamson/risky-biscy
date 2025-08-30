#!/bin/bash

echo "Building Risky Biscy executable..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH!"
    exit 1
fi

# Install requirements
echo "Installing requirements..."
pip3 install -r requirements.txt

# Build executable with PyInstaller
echo "Building executable..."
pyinstaller --onefile --windowed --name "RiskyBiscy" risky_biscy.py

# Check if build was successful
if [ -f "dist/RiskyBiscy" ]; then
    echo ""
    echo "==================================="
    echo "BUILD SUCCESSFUL!"
    echo "==================================="
    echo "Executable created: dist/RiskyBiscy"
    echo ""
    echo "You can now distribute this executable!"
else
    echo ""
    echo "BUILD FAILED!"
    echo "Check the output above for errors."
fi
