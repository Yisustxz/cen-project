# Space Shooter - Juego Multijugador con gRPC

Este proyecto implementa un juego de disparos espacial con capacidades multijugador utilizando un cliente Python y un servidor Go conectados mediante gRPC.

## Descripción

Space Shooter es un juego 2D donde los jugadores controlan naves espaciales y deben evitar o destruir meteoritos que cruzan la pantalla. La arquitectura cliente-servidor permite que múltiples jugadores participen en la misma partida en tiempo real.

### Características

- **Motor personalizado**: Implementación propia basada en Pygame en el cliente
- **Arquitectura distribuida**: Cliente Python para UI y servidor Go para lógica de juego
- **Comunicación en tiempo real**: Mediante gRPC para baja latencia
- **Soporte multijugador**: Varios jugadores pueden unirse a una partida
- **Físicas y colisiones**: Sistema de hitboxes personalizables

## Estructura del Proyecto

- `docs/` - Documentación completa del proyecto
- `proto/` - Definiciones del protocolo gRPC
- `go-backend/` - Servidor backend en Go
- `python-game/` - Cliente del juego en Python
- `config.json` - Configuración global del juego
- `entities_config.json` - Configuración de entidades del juego

## Requisitos

### Cliente Python

- Python 3.10+
- Pygame 2.0+
- gRPC para Python

### Servidor Go

- Go 1.18+
- gRPC para Go

### Herramientas de desarrollo

- Protocol Buffers (protoc) 3.19.0+
- Generadores de código gRPC para Python y Go

## Instalación

### Preparación del entorno

1. **Instalar Protocol Buffers (protoc)**

   - Descargar desde [GitHub](https://github.com/protocolbuffers/protobuf/releases)
   - Extraer en una carpeta (ej: `C:\Program Files\protoc`)
   - Añadir al PATH la ruta `C:\Program Files\protoc\bin`

2. **Instalar Go**

   - Descargar desde [go.dev](https://go.dev/dl/)
   - Verificar la instalación: `go version`

3. **Instalar Python**
   - Descargar desde [python.org](https://www.python.org/downloads/)
   - Verificar la instalación: `python --version`

### Configuración del proyecto

1. **Clonar el repositorio**

   ```
   git clone https://github.com/usuario/space-shooter.git
   cd space-shooter
   ```

2. **Instalar dependencias de Go**

   ```
   go mod download
   ```

3. **Instalar dependencias de Python**

   ```
   cd python-game
   pip install -r requirements.txt
   cd ..
   ```

4. **Compilar los archivos proto**
   - Windows: `proto\compile_protos.bat`
   - Linux/Mac: `chmod +x proto/compile_protos.sh && ./proto/compile_protos.sh`

## Ejecución

### Iniciar el servidor

```
cd go-backend/cmd/server
go run main.go
```

### Iniciar el cliente

```
cd python-game/src
python main.py
```

## Modos de Juego

- **Modo un jugador**: Juega localmente sin conexión al servidor
- **Modo multijugador**: Conéctate a un servidor y juega con otros jugadores

## Arquitectura

El proyecto utiliza una arquitectura cliente-servidor:

- **Cliente Python**:

  - Motor de juego basado en Pygame
  - Implementación de UI y entrada de usuario
  - Cliente gRPC para comunicación con el servidor

- **Servidor Go**:
  - Implementación de la lógica central del juego
  - Motor de física y colisiones
  - Sincronización de estados entre clientes

Para más detalles, consulta la documentación completa en:

- [Guía del Motor de Juego](docs/motor-guide.md)
- [Arquitectura Multijugador](docs/arquitectura_multiplayer.md)

## Desarrollo

### Generación de Código gRPC

Si modificas los archivos `.proto`, necesitarás regenerar el código:

- Windows: `proto\compile_protos.bat`
- Linux/Mac: `./proto/compile_protos.sh`

### Configuración del Juego

La configuración se carga desde:

- `config.json` - Configuración general y de red
- `entities_config.json` - Configuración de entidades (hitboxes, velocidades, etc.)

## Contribuir

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
