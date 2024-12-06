::
:: Ricevute - Invoice Management System Launcher
:: This batch file sets up and runs the invoice management application
::

@echo off
setlocal EnableDelayedExpansion

:: Set the working directory to the script's location
cd /d "%~dp0"

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Start logging
echo Starting Ricevute launcher at %date% %time%

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate the virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install dependencies if needed
if not exist "venv\Lib\site-packages\reportlab" (
    echo Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

:: Add the current directory to PYTHONPATH
set PYTHONPATH=%CD%;%PYTHONPATH%

:: Try to start with pythonw first (no console window)
echo Starting application...
start "" /B pythonw -m src

:: Wait a moment to check if the application started
timeout /t 2 > nul

:: Check if pythonw is running and if the main window is visible
tasklist /FI "IMAGENAME eq pythonw.exe" | find "pythonw.exe" > nul
if errorlevel 1 (
    echo Application failed to start with pythonw
    echo Trying with regular python for debugging...
    
    :: Kill any existing pythonw processes from failed starts
    taskkill /F /IM pythonw.exe > nul 2>&1
    
    :: Start with regular python for debugging
    python -m src
    if errorlevel 1 (
        echo Application failed to start
        echo Check the logs directory for error details
        pause
        exit /b 1
    )
)