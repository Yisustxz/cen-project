#!/bin/bash

# Configuración de rutas
PROTO_DIR="."
GO_OUT_DIR="../backend/internal/service"
PYTHON_OUT_DIR="../python-game/src/space_shooter/networking/generated"

# Crear directorio de salida si no existe
mkdir -p "$GO_OUT_DIR"
mkdir -p "$PYTHON_OUT_DIR"
touch "$PYTHON_OUT_DIR/__init__.py"
echo "Creado archivo __init__.py en el directorio de salida de Python"

# Exportar PATH para asegurar que se encuentran los binarios
export PATH=$PATH:$HOME/go/bin

# Compilar para Go
echo "Compilando protos para Go..."
protoc --go_out="$GO_OUT_DIR" --go_opt=paths=source_relative \
       --go-grpc_out="$GO_OUT_DIR" --go-grpc_opt=paths=source_relative \
       -I "$PROTO_DIR" "$PROTO_DIR/game.proto"

# Verificar resultado
if [ $? -ne 0 ]; then
    echo "Error al compilar los Protocol Buffers para Go."
    exit 1
fi

# Compilar para Python
echo "Compilando protos para Python..."
python3 -m grpc_tools.protoc -I"$PROTO_DIR" --python_out="$PYTHON_OUT_DIR" \
         --grpc_python_out="$PYTHON_OUT_DIR" "$PROTO_DIR/game.proto"

# Verificar resultado
if [ $? -ne 0 ]; then
    echo "Error al compilar los Protocol Buffers para Python."
    exit 1
fi

# Solución para modificar imports en Python
if [ -f "$PYTHON_OUT_DIR/game_pb2_grpc.py" ]; then
    echo "Ajustando imports en Python..."
    sed -i 's/import game_pb2/from space_shooter.networking.generated import game_pb2/g' "$PYTHON_OUT_DIR/game_pb2_grpc.py"
fi

echo
echo "¡Protocol Buffers compilados exitosamente!"
echo "- Archivos Go generados en: $GO_OUT_DIR"
echo "- Archivos Python generados en: $PYTHON_OUT_DIR"
echo 