Proyecto de Computacion en la nube para videojuego con grpc:

## Estructura

- `proto/` - Definiciones .proto
- `backend/` - Servidor Go
- `frontend/` - Cliente Python

se necesita
go version go1.24.2 windows/amd64
python 3.12.8
protoc 25.7

Para el protoc al descargar el .zip hay que extraerlo en una carpeta llamada protoc en program files (crear la carpeta protoc) y agregarlo al PATH la ruta hacia protoc\bin

para go hay que hacer go mod download en root del Proyecto

para python hay que entrar en la carpeta frontend y ejecutar pip install -r requirements.txt

al tener todo eso listo lo primero que se ejecuta es el archive .bat desde root se haria de la siguiente manera proto\compile_protos.bat (esto funciona en windows, hay que versionar esto para Linux Tambien), esto generara los compilados necesarios para ejecutar el Proyecto

luego se ejecuta dentro de backend/server el Proyecto de go con go run main.go y en frotend/client client.py y listo
