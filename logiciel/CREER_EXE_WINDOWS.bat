@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Cet outil cree un EXE sur ton propre ordinateur Windows.
echo Python et une connexion Internet seront necessaires.
echo Pour inclure OBD2 reel, lancer INSTALLER_OBD2.bat AVANT cet outil.
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m pip install --upgrade "pyinstaller>=6.0,<7.0"
  if errorlevel 1 goto failed
  py -3 -m PyInstaller --onefile --windowed --clean --noconfirm --name "VM_Performance_Atelier" --hidden-import dossiers_cles --hidden-import remplacement_cles vm_performance.py
) else (
  python -m pip install --upgrade "pyinstaller>=6.0,<7.0"
  if errorlevel 1 goto failed
  python -m PyInstaller --onefile --windowed --clean --noconfirm --name "VM_Performance_Atelier" --hidden-import dossiers_cles --hidden-import remplacement_cles vm_performance.py
)
if errorlevel 1 goto failed
echo.
echo EXE cree dans le dossier dist\VM_Performance_Atelier.exe
pause
exit /b 0
:failed
echo ERREUR : lire les messages ci-dessus. Aucun EXE garanti avant test.
pause
exit /b 1
