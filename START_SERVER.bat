@echo off
chcp 65001 >nul
title DeepFake Reconstruction & Detection System
cd /d "%~dp0deepfake_reconstruction"
echo.
echo ============================================================
echo   DEEPFAKE RECONSTRUCTION & DETECTION SYSTEM
echo   Identity-Preserving Face Reconstruction using MAE
echo   Serving on: http://127.0.0.1:8000/
echo   Press Ctrl+C to stop.
echo ============================================================
echo.
python manage.py runserver 127.0.0.1:8000
echo.
echo Server stopped.
pause
