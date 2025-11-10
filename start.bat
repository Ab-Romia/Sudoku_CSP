@echo off
echo 🚀 Starting Sudoku AI Solver...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✓ Python is installed

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo.
echo 🌐 Starting Flask server...
echo Server will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
pause
