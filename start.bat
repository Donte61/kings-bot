@echo off
echo.
echo ==================================================
echo    King Bot Pro v2.0.0 - Modern Edition
echo    Hizli Baslatici (Windows)
echo ==================================================
echo.

REM Python'un yuklu olup olmadigini kontrol et
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo HATA: Python bulunamadi!
    echo Lutfen Python 3.8+ yukleyin: https://python.org
    echo.
    pause
    exit /b 1
)

echo Python bulundu, baslatiliyor...
echo.

REM Uygulamayi baslat
python start.py

if %errorlevel% neq 0 (
    echo.
    echo HATA: Uygulama baslatma hatasi!
    echo.
)

pause
