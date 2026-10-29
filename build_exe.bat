@echo off
setlocal
echo ========================================================
echo   Building win-junction-scout Standalone Executable (.exe)
echo ========================================================

python -m pip install --upgrade pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install or verify PyInstaller.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Compiling win-junction-scout.exe...
python -m PyInstaller --onefile --clean --name win-junction-scout junction_scout.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   BUILD SUCCESSFUL!
    echo   Standalone executable created at:
    echo   dist\win-junction-scout.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] PyInstaller compilation failed.
)
endlocal
