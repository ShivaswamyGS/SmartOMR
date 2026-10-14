@echo off
title Push SmartOMR to GitHub
echo ==============================================================================
echo                Pushing SmartOMR to https://github.com/ShivaswamyGS/SmartOMR
echo ==============================================================================
echo.
echo Make sure you have created the empty repository "SmartOMR" at:
echo   https://github.com/new
echo.
echo Press any key to push now...
pause >nul
echo.
echo Pushing code to GitHub...
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ==============================================================================
    echo [SUCCESS] Code successfully pushed to https://github.com/ShivaswamyGS/SmartOMR!
    echo ==============================================================================
) else (
    echo ==============================================================================
    echo [NOTICE] If you saw 'Repository not found', please make sure the repository
    echo 'SmartOMR' is created on https://github.com/new (leave it empty, without README).
    echo ==============================================================================
)
echo.
pause
