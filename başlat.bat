@echo off
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo === HATA OLUSTU ===
    echo crash_report.txt dosyasini kontrol edin.
    pause
)
