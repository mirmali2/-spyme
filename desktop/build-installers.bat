@echo off
:: SPYME — One-shot laptop installer builder
:: Outputs: dist/SPYME-Setup.exe (Windows NSIS installer)
::          dist/SPYME-{version}.dmg (macOS, only if run on Mac)
:: No code signing (free). Users see one "Run anyway" warning on first launch.

echo ========================================
echo SPYME Laptop Installer Builder
echo ========================================

cd /d "%~dp0"

echo.
echo [1/3] Installing dependencies...
call npm install

echo.
echo [2/3] Building Windows installer (.exe)...
call npx electron-builder --win --x64 --publish never

echo.
echo [3/3] Done.
echo.
echo Output: %~dp0dist\
dir dist
echo.
echo Upload SPYME-Setup-*.exe to GitHub Releases for free distribution.
pause
