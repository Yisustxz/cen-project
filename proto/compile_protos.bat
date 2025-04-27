@echo off
SETLOCAL

:: Configuración de rutas
SET PROTO_DIR=.\proto
SET GO_OUT_DIR=.\backend\internal\service
SET PYTHON_OUT_DIR=.\frontend\generated

:: Compilar para Go
protoc --go_out=%GO_OUT_DIR% --go_opt=paths=source_relative ^
       --go-grpc_out=%GO_OUT_DIR% --go-grpc_opt=paths=source_relative ^
       -I %PROTO_DIR% %PROTO_DIR%\game.proto

:: Compilar para Python
python -m grpc_tools.protoc -I%PROTO_DIR% --python_out=%PYTHON_OUT_DIR% ^
         --grpc_python_out=%PYTHON_OUT_DIR% %PROTO_DIR%\game.proto

:: Solución para modificar imports sin sed
:: Método 1: Usar reemplazo nativo de batch (para archivos pequeños)
IF EXIST "%PYTHON_OUT_DIR%\game_pb2_grpc.py" (
    powershell -Command "(Get-Content '%PYTHON_OUT_DIR%\game_pb2_grpc.py') -replace '^import game_pb2', 'from generated import game_pb2' | Set-Content '%PYTHON_OUT_DIR%\game_pb2_grpc.py'"
)

:: Método alternativo 2: Usar archivo temporal
:: IF EXIST "%PYTHON_OUT_DIR%\game_pb2_grpc.py" (
::     (echo from generated import game_pb2 as game__pb2) > "%PYTHON_OUT_DIR%\temp.py"
::     more "%PYTHON_OUT_DIR%\game_pb2_grpc.py" | findstr /v "import game_pb2 as" >> "%PYTHON_OUT_DIR%\temp.py"
::     move /Y "%PYTHON_OUT_DIR%\temp.py" "%PYTHON_OUT_DIR%\game_pb2_grpc.py"
:: )

echo.
echo ¡Protocol Buffers compilados exitosamente!
echo - Archivos Go generados en: %GO_OUT_DIR%
echo - Archivos Python generados en: %PYTHON_OUT_DIR%
echo.

ENDLOCAL