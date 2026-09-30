@echo off
chcp 65001 >nul
title DeepShield AI - Deepfake Detection Server
cd /d "d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
echo.
echo ============================================================
echo   DEEPSHIELD AI SERVER
echo   Serving on: http://127.0.0.1:8000/
echo   Press Ctrl+C to stop.
echo ============================================================
echo.
python manage.py runserver 0.0.0.0:8000 --noreload
echo.
echo Server stopped.
pause
