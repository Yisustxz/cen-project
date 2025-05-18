#!/bin/bash

# Configuración de rutas
PROTO_DIR="./proto"
GO_OUT_DIR="./backend/internal/service"
PYTHON_OUT_DIR="./python-game/src/space_shooter/networking/generated"

# Verificar e instalar dependencias
if ! command -v protoc &> /dev/null; then
    echo "Error: protoc no está instalado"
    echo "Instálalo con: sudo apt install protobuf-compiler"
    exit 1
fi

# Verificar la versión de Go
GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
echo "Versión de Go detectada: $GO_VERSION"

# Intentar instalar versiones específicas compatibles con Go 1.18
if ! command -v protoc-gen-go &> /dev/null; then
    echo "Error: protoc-gen-go no está instalado"
    echo "Instalando versiones específicas compatibles con Go 1.18..."
    go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28.1
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2.0
    
    # Verificar que la instalación fue exitosa y añadir al PATH
    if [ $? -eq 0 ]; then
        echo "Agregando $HOME/go/bin al PATH temporalmente..."
        export PATH=$PATH:$HOME/go/bin
    else
        echo "Error al instalar protoc-gen-go. Por favor, instala manualmente:"
        echo "GO111MODULE=on go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28.1"
        echo "GO111MODULE=on go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2.0"
        echo "Luego ejecuta: export PATH=\$PATH:\$HOME/go/bin"
        exit 1
    fi
fi

# Verificar que protoc-gen-go está en el PATH
if ! command -v protoc-gen-go &> /dev/null; then
    echo "Error: protoc-gen-go no está en el PATH a pesar de la instalación"
    echo "Agrega manualmente con: export PATH=\$PATH:\$HOME/go/bin"
    echo "Luego vuelve a ejecutar este script"
    exit 1
fi

# Instalar grpc_tools para Python si es necesario
if ! python3 -c "import grpc_tools" &> /dev/null; then
    echo "Instalando grpc_tools para Python..."
    pip3 install grpcio-tools
    if [ $? -ne 0 ]; then
        echo "Error al instalar grpcio-tools. Intenta manualmente:"
        echo "pip3 install grpcio-tools"
        exit 1
    fi
fi

# Verificar que existan las carpetas
mkdir -p "$GO_OUT_DIR"
mkdir -p "$PYTHON_OUT_DIR"
touch "$PYTHON_OUT_DIR/__init__.py"
echo "Creado archivo __init__.py en el directorio de salida de Python"

# Compilar para Go
echo "Compilando protos para Go..."
protoc --go_out="$GO_OUT_DIR" --go_opt=paths=source_relative \
       --go-grpc_out="$GO_OUT_DIR" --go-grpc_opt=paths=source_relative \
       -I "$PROTO_DIR" "$PROTO_DIR/game.proto"

# Verificar que la compilación para Go fue exitosa
if [ $? -ne 0 ]; then
    echo "Error al compilar los Protocol Buffers para Go."
    exit 1
fi

# Compilar para Python
echo "Compilando protos para Python..."
python3 -m grpc_tools.protoc -I"$PROTO_DIR" --python_out="$PYTHON_OUT_DIR" \
         --grpc_python_out="$PYTHON_OUT_DIR" "$PROTO_DIR/game.proto"

# Verificar que la compilación para Python fue exitosa
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
