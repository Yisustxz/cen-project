#!/bin/bash

# Navegar al directorio backend
cd "$(dirname "$0")/backend"

# Compilar el servidor (opcional, comentar si prefieres usar go run)
# go build -o server

# Ejecutar el servidor
go run main.go

# Si prefieres ejecutar el binario compilado, usa esta línea en lugar de la anterior
# ./server 