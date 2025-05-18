#!/bin/bash

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

# Verificar si hay algún proceso usando el puerto 9090
if lsof -i :9090 > /dev/null; then
    echo "¡ADVERTENCIA! El puerto 9090 ya está en uso. Intentando matar el proceso..."
    sudo kill $(lsof -t -i:9090)
    sleep 1
    if lsof -i :9090 > /dev/null; then
        echo "ERROR: No se pudo liberar el puerto 9090. Por favor, cierre manualmente la aplicación que lo está usando."
        exit 1
    fi
fi

# Asegurarse de que el directorio backend tenga acceso al archivo de configuración
echo "Copiando archivo de configuración al directorio backend..."
cp config.json backend/

# Ejecutar el servidor y redirigir la salida a un archivo
echo "Iniciando servidor Space Shooter en localhost:9090..."
echo "---------------------------------------------------"
cd backend && ./server_binary 2>&1 | tee ../server_log.txt

# Verificar si hubo errores
if [ $? -ne 0 ]; then
    echo "¡ERROR! El servidor terminó con código de error. Consulte server_log.txt para más detalles."
    exit 1
fi 