@echo off
title Hammer Pro — EXE Builder
echo.
echo  =============================================
echo   HAMMER PRO  EXE Olusturucu
echo  =============================================
echo.
pip install pyinstaller pywin32 --quiet
echo.
echo  EXE olusturuluyor...
pyinstaller --onefile --noconsole ^
  --name "HammerProLookup_v8" ^
  --add-data "data;data" ^
  app.py
echo.
echo  HAZIR: dist\HammerProLookup_v8.exe
echo.
echo  ONEMLI: dist\ klasorunu data\ ile birlikte tasiyin!
echo          HammerProLookup_v8.exe yaninda data\ klasoru olmali.
echo.
pause
