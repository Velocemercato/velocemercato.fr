@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 vm_performance.py
) else (
    python vm_performance.py
)
if errorlevel 1 (
    echo.
    echo Python 3 avec Tkinter est necessaire. Voir LISEZ_MOI.txt.
    pause
)
