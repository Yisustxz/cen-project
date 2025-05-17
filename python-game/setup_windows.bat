@echo off
REM setup_windows.bat
REM Script para configurar entorno virtual y dependencias en Windows

python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo Entorno virtual activado y dependencias instaladas. Ejecuta:
echo python src/main.py
