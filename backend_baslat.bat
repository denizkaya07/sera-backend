@echo off
title Sera Backend
cd /d "%~dp0"

echo [1/4] Sanal ortam aktif ediliyor...
call venv\Scripts\activate
if errorlevel 1 (
    echo HATA: venv bulunamadi. Klasor yapisi kontrol edin.
    pause
    exit /b 1
)

echo [2/4] Eksik paketler yukleniyor...
pip install reportlab -q

echo [3/4] Veritabani guncelleniyor (migrate)...
python manage.py migrate

echo [4/4] Sunucu basliyor: http://127.0.0.1:8000
echo Durdurmak icin CTRL+C
echo.
python manage.py runserver
pause
