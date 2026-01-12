@echo off
echo ========================================
echo Plex Poster Set Helper - Setup Script
echo ========================================
echo.

python setup.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Setup failed! Please check the error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Press any key to exit...
pause >nul
