@echo off
echo ========================================================
echo  X Auto Poster - Browser Installer
echo ========================================================
echo.
echo This script installs the necessary browsers for the app.
echo It only needs to be run ONCE on this computer.
echo.

echo Installing Playwright browsers...
REM We need to use the internal python of the app if possible, 
REM but since it's a onefile exe, we can't easily access it.
REM So we assume the user has Python installed OR we rely on the onefile app to do it?
REM Actually, for a "v1.0 style" distribution where the user might not have Python:
REM The robust way is to let the APP install it, but the app is crashing.
REM So we assume the user has Python installed (as per requirements).

python -m pip install playwright
python -m playwright install chromium firefox

echo.
echo Done! You can now run X_Auto_Poster.exe.
pause
