@echo off
chcp 65001 >nul
title DeepFake Reconstruction & Detection System
echo.
echo ============================================================
echo   DEEPFAKE RECONSTRUCTION & DETECTION SYSTEM
echo   Identity-Preserving Face Reconstruction using MAE
echo ============================================================
echo.
echo Starting Django Web Application...
echo Access URL: http://127.0.0.1:8000/
echo Press Ctrl+C in this window to stop the server.
echo.
python manage.py runserver 127.0.0.1:8000
pause
