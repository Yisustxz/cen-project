#!/bin/bash
# setup_linux.sh
# Script para configurar entorno virtual y dependencias en Linux/Mac

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo -e "\nEntorno virtual activado y dependencias instaladas. Ejecuta:"
echo "python src/main.py"
