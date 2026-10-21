@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Installation de la bibliotheque de lecture OBD2 (internet requis).
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m pip install "obd==0.7.3"
) else (
    python -m pip install "obd==0.7.3"
)
echo.
echo Installation terminee (verifiez les erreurs ci-dessus).
pause
