@echo off
title Hammer Pro — Preferred Lookup v8
color 0B
echo.
echo  =============================================
echo   HAMMER PRO  Preferred Lookup  v8
echo  =============================================
echo.
echo  Gerekli paketler kontrol ediliyor...
pip install pywin32 --quiet 2>nul
echo  Baslatiliyor...
echo.
pythonw app.py
if %errorlevel% neq 0 (
    echo.
    echo  [!] Hata olustu. Python yuklu mu?
    echo      https://python.org
    pause
)
