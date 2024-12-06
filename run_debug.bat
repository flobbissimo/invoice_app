::
:: Ricevute - Invoice Management System Debug Launcher
:: This batch file provides detailed debugging information and error handling
::

@echo off
setlocal EnableDelayedExpansion

:: Set console title
title Ricevute Debug Launcher

:: Set the working directory to the script's location
cd /d "%~dp0"

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Start debug log
set "debug_log=logs\debug_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"
set "debug_log=%debug_log: =0%"

echo =============================================== > "%debug_log%"
echo Ricevute Debug Launcher >> "%debug_log%"
echo Started at: %date% %time% >> "%debug_log%"
echo =============================================== >> "%debug_log%"
echo. >> "%debug_log%"

:: Function to log messages
call :log "Starting debug launcher..."
call :log "Current directory: %CD%"

:: Check Python version and installation
call :log "Checking Python installation..."
python --version > temp.txt 2>&1
set /p PYTHON_VERSION=<temp.txt
del temp.txt

if errorlevel 1 (
    call :log "ERROR: Python is not installed or not in PATH"
    echo Please install Python from python.org
    pause
    exit /b 1
)
call :log "Found Python version: %PYTHON_VERSION%"

:: Check pip installation
call :log "Checking pip installation..."
python -m pip --version > temp.txt 2>&1
set /p PIP_VERSION=<temp.txt
del temp.txt
call :log "Found pip version: %PIP_VERSION%"

:: Check system environment
call :log "System Information:"
call :log "  OS: %OS%"
call :log "  PROCESSOR_ARCHITECTURE: %PROCESSOR_ARCHITECTURE%"
call :log "  NUMBER_OF_PROCESSORS: %NUMBER_OF_PROCESSORS%"
call :log "  PYTHONPATH: %PYTHONPATH%"

:: Remove old virtual environment if it exists
if exist "venv" (
    call :log "Removing old virtual environment..."
    rmdir /s /q "venv"
    if errorlevel 1 (
        call :log "ERROR: Failed to remove old virtual environment"
        pause
        exit /b 1
    )
)

:: Create fresh virtual environment
call :log "Creating new virtual environment..."
python -m venv venv
if errorlevel 1 (
    call :log "ERROR: Failed to create virtual environment"
    pause
    exit /b 1
)

:: Activate virtual environment
call :log "Activating virtual environment..."
call venv\Scripts\activate.bat
if errorlevel 1 (
    call :log "ERROR: Failed to activate virtual environment"
    pause
    exit /b 1
)

:: Install dependencies
call :log "Installing dependencies..."
python -m pip install --upgrade pip
call :log "Upgraded pip to latest version"

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    call :log "ERROR: requirements.txt not found"
    pause
    exit /b 1
)

:: Install requirements with detailed output
pip install -r requirements.txt
if errorlevel 1 (
    call :log "ERROR: Failed to install dependencies"
    pause
    exit /b 1
)
call :log "Successfully installed all dependencies"

:: Check for required directories and files
call :log "Checking required files and directories..."
if not exist "src" (
    call :log "ERROR: src directory not found"
    pause
    exit /b 1
)

if not exist "config" mkdir config
call :log "Ensured config directory exists"

:: Add the current directory to PYTHONPATH
set PYTHONPATH=%CD%;%PYTHONPATH%
call :log "Updated PYTHONPATH: %PYTHONPATH%"

:: Run application in debug mode
call :log "Starting application in debug mode..."
echo.
echo ===============================================
echo Debug Console Output
echo ===============================================
echo.

:: Run with exception handling
python -m src 2>> "%debug_log%"
set EXIT_CODE=%errorlevel%

echo.
echo ===============================================
if %EXIT_CODE% EQU 0 (
    echo Application closed normally.
    call :log "Application closed normally"
) else (
    echo Application exited with error code: %EXIT_CODE%
    call :log "ERROR: Application exited with code %EXIT_CODE%"
)
echo ===============================================
echo.
echo Debug log saved to: %debug_log%
echo.
if %EXIT_CODE% NEQ 0 (
    echo Please check the debug log for error details.
)

pause
exit /b %EXIT_CODE%

:: Log function
:log
echo %~1
echo %date% %time% - %~1 >> "%debug_log%"
goto :eof 