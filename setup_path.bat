@echo off
setlocal EnableDelayedExpansion

echo ==========================================
echo            AUV File Organizer
echo           Quick Setup Script
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version

echo.
echo [INFO] Installing dependencies...
pip install --user watchdog>=2.1.0 psutil>=5.8.0 click>=8.0.0
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [INFO] Installing AUV...
pip install --user -e .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install AUV
    pause
    exit /b 1
)

echo.
echo [INFO] Configuring environment variables...

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do set PY_MAJOR=%%a&set PY_MINOR=%%b

:: Build Scripts path
set "SCRIPTS_PATH=%APPDATA%\Python\Python%PY_MAJOR%%PY_MINOR%\Scripts"

:: Check if path exists
if not exist "%SCRIPTS_PATH%" (
    echo [WARN] Scripts directory not found: %SCRIPTS_PATH%
    echo [INFO] Searching for alternative paths...
    
    :: Find all possible Python Scripts directories
    for /d %%d in ("%APPDATA%\Python\Python*\Scripts") do (
        if exist "%%d" (
            set "SCRIPTS_PATH=%%d"
            echo [OK] Found Scripts directory: !SCRIPTS_PATH!
            goto :found_scripts
        )
    )
    
    echo [ERROR] Cannot find Python Scripts directory
    echo [INFO] Please manually add this path to PATH environment variable:
    echo %APPDATA%\Python\Python%PY_MAJOR%%PY_MINOR%\Scripts
    pause
    exit /b 1
)

:found_scripts
:: Check if already in PATH
echo %PATH% | findstr /i "%SCRIPTS_PATH%" >nul
if %errorlevel% == 0 (
    echo [OK] Environment variable already configured
    goto :test_command
)

:: Add to user PATH
echo [INFO] Adding to user PATH: %SCRIPTS_PATH%
for /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH 2^>nul') do set "USER_PATH=%%b"
if defined USER_PATH (
    setx PATH "%USER_PATH%;%SCRIPTS_PATH%"
) else (
    setx PATH "%SCRIPTS_PATH%"
)

if %errorlevel% == 0 (
    echo [OK] Environment variable configured successfully
) else (
    echo [ERROR] Failed to configure environment variable
    echo [INFO] Please manually add this path: %SCRIPTS_PATH%
)

:test_command
echo.
echo [INFO] Testing installation...

:: Update PATH for current session
set "PATH=%PATH%;%SCRIPTS_PATH%"

:: Test auv command
auv --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] AUV installed successfully!
    echo.
    auv --version
) else (
    echo [WARN] Command test failed, may need to restart command prompt
    echo [INFO] If problem persists, check if this path is in PATH:
    echo %SCRIPTS_PATH%
)

echo.
echo ==========================================
echo            Setup Complete!
echo ==========================================
echo.
echo Usage Examples:
echo   auv --help               # Show help
echo   auv status               # Show current status
echo   auv -pdf                 # Organize PDFs in current folder
echo   auv -d -pdf              # Organize PDFs in downloads folder
echo   auv here -pdf            # Create PDF folder in current directory
echo   auv set downloads "path" # Set downloads folder path
echo.
echo [TIP] If commands don't work, restart your command prompt
echo.
pause