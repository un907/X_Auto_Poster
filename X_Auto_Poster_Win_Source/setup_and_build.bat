@echo off
setlocal enabledelayedexpansion
chcp 65001
echo ========================================================
echo  X Auto Poster - Full Build & Installer Script
echo ========================================================
echo.

:: --- 1. Environment Check ---
echo [1/5] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.12+.
    pause
    exit /b
)

:: --- 2. Virtual Environment Setup ---
echo.
echo [2/5] Setting up Virtual Environment...
if not exist venv (
    echo Creating venv...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

:: --- 3. Browser Download (Critical for Installer) ---
echo.
echo [3/5] Downloading Browsers for Bundling...
:: Set path to dist/browsers so PyInstaller/InnoSetup can find them
set "DIST_BROWSER_DIR=%~dp0dist\browsers"
if not exist "%DIST_BROWSER_DIR%" mkdir "%DIST_BROWSER_DIR%"

echo Target Dir: %DIST_BROWSER_DIR%
set PLAYWRIGHT_BROWSERS_PATH=%DIST_BROWSER_DIR%
playwright install chromium firefox

:: --- 4. Build Executable (PyInstaller) ---
echo.
echo [4/5] Building EXE with PyInstaller...
:: Note: We rely on Inno Setup to bundle the browsers, so we don't add them here.
pyinstaller --noconfirm --onefile --windowed --name "X_Auto_Poster" ^
 --add-data "settings.json;." ^
 --add-data "personas.json;." ^
 --add-data "accounts.csv;." ^
 --hidden-import=customtkinter ^
 --hidden-import=google.generativeai ^
 main.py

if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller failed.
    pause
    exit /b
)

:: --- 5. Compile Installer (Inno Setup) ---
echo.
echo [5/5] Compiling Installer with Inno Setup (Optional)...

:: Try to find ISCC.exe (Standard Paths)
set "ISCC_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if defined ISCC_PATH (
    echo Found Inno Setup Compiler: "!ISCC_PATH!"
    "!ISCC_PATH!" "setup.iss"
) else (
    echo [WARNING] Inno Setup Compiler not found. Skipping Installer creation.
)

:: --- 6. Create Zip Package (Primary Distribution) ---
echo.
echo [6/6] Creating Zip Package...

set "PACKAGE_DIR=Output\Package_v1.8.2"
set "ZIP_FILE=Output\X_Auto_Poster_v1.8.2.zip"

if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

:: Copy Files
echo Copying files...
copy "dist\X_Auto_Poster.exe" "%PACKAGE_DIR%\" >nul
xcopy "dist\browsers" "%PACKAGE_DIR%\browsers\" /E /I /Y >nul
copy "最初に読んで下さい.txt" "%PACKAGE_DIR%\" >nul
if exist "..\manual.html" copy "..\manual.html" "%PACKAGE_DIR%\" >nul

:: Create Zip using PowerShell
echo Zipping...
powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force"

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! Build Complete.
    echo.
    echo  [Zip Package] %ZIP_FILE%
    echo  (Contains: exe, browsers, readme, manual)
    echo.
    if exist "Output\X_Auto_Poster_Setup_v1.8.2.exe" (
        echo  [Installer] Output\X_Auto_Poster_Setup_v1.8.2.exe
    )
    echo ========================================================
) else (
    echo [ERROR] Zip creation failed.
)

pause
