# Servidor Space Shooter

Este es el servidor para la versión multijugador del juego Space Shooter.

## Requisitos

- Go 1.19+
- Protobuf Compiler (protoc)
- Go gRPC plugins
  - `go install google.golang.org/protobuf/cmd/protoc-gen-go@latest`
  - `go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest`

## Compilar los archivos Protocol Buffers

### En Windows

```
backend\compile_protos.bat
```

### En Linux/Mac

```
chmod +x backend/compile_protos.sh
./backend/compile_protos.sh
```

## Ejecutar el servidor

Desde el directorio raíz del proyecto:

```
cd backend
go run main.go
```

## Configuración

El servidor utiliza la configuración en `config.json` que se encuentra en la raíz del proyecto. Asegúrate de que los valores `backend.ip` y `backend.port` estén configurados correctamente.
