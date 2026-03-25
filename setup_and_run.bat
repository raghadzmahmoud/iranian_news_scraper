@echo off
REM Setup and Run X Scraper Locally (Windows)
REM تجهيز وتشغيل السحب من X محليًا

setlocal enabledelayedexpansion

echo ==================================================
echo 🔧 X Scraper Local Setup ^& Run (Windows)
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%

REM Check if venv exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade requirements
echo 📥 Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright browsers
echo 🌐 Installing Playwright browsers...
python -m playwright install chromium

REM Run the scraper
echo.
echo ==================================================
echo 🚀 Starting X Scraper...
echo ==================================================
echo.

python run_x_scraper_local.py

echo.
echo ==================================================
echo ✅ Done!
echo ==================================================

pause
