# Arquitectura del Sistema Multijugador

Este documento describe la arquitectura del sistema multijugador para Space Shooter, detallando la integración entre el cliente Python y el servidor backend en Go mediante gRPC.

## Índice

1. [Visión General](#visión-general)
2. [Componentes del Sistema](#componentes-del-sistema)
3. [Comunicación gRPC](#comunicación-grpc)
4. [Arquitectura del Servidor Go](#arquitectura-del-servidor-go)
5. [Arquitectura del Cliente Python](#arquitectura-del-cliente-python)
6. [Sincronización de Estado](#sincronización-de-estado)
7. [Manejo de Eventos](#manejo-de-eventos)
8. [Gestión de Objetos](#gestión-de-objetos)
9. [Consideraciones de Rendimiento](#consideraciones-de-rendimiento)
10. [Plan de Implementación](#plan-de-implementación)

## Visión General

El sistema multijugador para Space Shooter permite a múltiples jugadores participar en una partida compartida. La arquitectura se basa en un modelo cliente-servidor:

- **Servidor Go**: Motor de juego que ejecuta la lógica principal
- **Cliente Python**: Interfaz gráfica y entrada del usuario

```
┌─────────────────┐                             ┌─────────────────┐
│                 │       gRPC Stream           │                 │
│  Cliente        │◄────────────────────────────┤  Servidor       │
│  Python         │                             │  Go             │
│                 │                             │                 │
│  (Renderizado,  │                             │  (Lógica de     │
│   Input)        │─────────────────────────────►  juego,         │
│                 │       gRPC Calls            │   Física)       │
└─────────────────┘                             └─────────────────┘
```

### Principios Fundamentales

1. **Autoridad del servidor**: El servidor es la autoridad final sobre el estado del juego
2. **Predicción del cliente**: Los clientes predicen el movimiento para una experiencia fluida
3. **Reconciliación**: El servidor corrige las discrepancias entre su estado y las predicciones
4. **Identificadores únicos**: Cada objeto tiene un ID global único para seguimiento

## Componentes del Sistema

### Servidor Go (Backend)

- **Motor del juego**: Reimplementación de la lógica principal en Go
- **Gestor de salas**: Administra partidas y jugadores conectados
- **Servidor gRPC**: Maneja conexiones y comunicación
- **Sistema de eventos**: Transmite cambios de estado a los clientes

### Cliente Python (Frontend)

- **Motor gráfico existente**: Renderizado, UI y entrada
- **Adaptador de red**: Comunicación con el servidor
- **Sistema de reconciliación**: Maneja correcciones del servidor
- **Gestor de predicción**: Simula movimiento local antes de confirmación

## Comunicación gRPC

### Protocolo de Comunicación

El protocolo gRPC definido en `proto/game.proto` se expandirá para incluir:

```protobuf
syntax = "proto3";

package game;

service GameService {
  // Establece conexión de streaming bidireccional
  rpc JoinGame (stream ClientMessage) returns (stream ServerMessage);

  // RPC de un solo uso para operaciones específicas
  rpc SendInput (PlayerInput) returns (GameState);
}

// Mensaje contenedor para el cliente
message ClientMessage {
  oneof message {
    PlayerJoin player_join = 1;
    PlayerInput player_input = 2;
    HeartbeatPing heartbeat = 3;
  }
}

// Mensaje contenedor para el servidor
message ServerMessage {
  oneof message {
    GameState game_state = 1;
    EntityUpdate entity_update = 2;
    PlayerEvent player_event = 3;
    HeartbeatPong heartbeat = 4;
  }
}

// Detalles de un jugador al unirse
message PlayerJoin {
  string player_name = 1;
}

// Entrada del jugador
message PlayerInput {
  string player_id = 1;
  string action = 2;  // "LEFT", "RIGHT", "FIRE"
  int64 timestamp = 3;
  int32 sequence_number = 4;
}

// Estado del juego completo
message GameState {
  repeated Entity entities = 1;
  repeated Player players = 2;
  int32 state = 3;  // 0=esperando, 1=jugando, 2=game_over
  int64 server_time = 4;
}

// Actualización parcial de entidad
message EntityUpdate {
  string entity_id = 1;
  EntityType type = 2;
  oneof update {
    CreateEntity create = 3;
    UpdateEntity update = 4;
    DeleteEntity delete = 5;
  }
}

// Tipos de entidades
enum EntityType {
  PLAYER = 0;
  METEOR = 1;
  MISSILE = 2;
}

// Definiciones de entidades...
```

### Flujo de Comunicación

1. **Conexión inicial**:

   - Cliente inicia conexión con `JoinGame`
   - Envía `PlayerJoin` con información del jugador
   - Servidor responde con `GameState` completo

2. **Comunicación durante el juego**:
   - Cliente envía `PlayerInput` para cada acción del usuario
   - Servidor transmite `EntityUpdate` para creación/actualización/eliminación de entidades
   - Heartbeats periódicos para detección de desconexión

## Arquitectura del Servidor Go

### Estructura de Directorios

```
go-backend/
├── cmd/
│   └── server/
│       └── main.go               # Punto de entrada
├── internal/
│   ├── config/                   # Configuración
│   │   └── config.go            # Configuración
│   ├── game/                     # Lógica de juego
│   │   ├── engine.go             # Motor principal
│   │   ├── entity.go             # Entidades base
│   │   ├── player.go             # Jugador
│   │   ├── meteor.go             # Meteoritos
│   │   └── missile.go            # Misiles
│   ├── network/                  # Componentes de red
│   │   ├── server.go             # Servidor gRPC
│   │   └── room.go               # Gestor de salas
│   └── service/                  # Implementación gRPC
│       └── game_service.go       # Servicios definidos
└── pkg/
    ├── util/                     # Utilidades comunes
    │   └── delta_time.go         # Sistema de tiempo delta
    └── proto/                    # gRPC generado
```

### Componentes Principales

1. **GameEngine**:

   - Reimplementación del motor actual en Go
   - Maneja física, colisiones y eventos
   - Sistema de actualización basado en ticks

2. **Entity**:

   - Sistema base para objetos del juego
   - Contiene posición, velocidad, tipo y ID único

3. **Room**:

   - Gestiona una partida
   - Mantiene lista de jugadores
   - Coordina ciclo de juego

4. **GameServer**:
   - Implementa la interfaz gRPC
   - Gestiona conexiones de clientes
   - Distribuye eventos a clientes conectados

### Ciclo de Actualización del Servidor

```go
// Pseudocódigo del ciclo de actualización
func (g *GameRoom) Run() {
    ticker := time.NewTicker(16 * time.Millisecond) // ~60fps

    for {
        select {
        case <-ticker.C:
            // Calcular delta time
            deltaTime := g.deltaTimer.GetDelta()

            // Procesar entradas pendientes de jugadores
            g.processPlayerInputs()

            // Actualizar todos los objetos
            g.updateEntities(deltaTime)

            // Detectar colisiones
            g.detectCollisions()

            // Enviar actualizaciones a clientes
            g.broadcastUpdates()

        case <-g.stopChan:
            ticker.Stop()
            return
        }
    }
}
```

## Arquitectura del Cliente Python

### Estructura de Directorios

```
python-game/
└── src/
    ├── space_shooter/
    │   └── networking/
    │       ├── client.py               # Cliente gRPC
    │       ├── server_proxy.py         # Proxy del servidor
    │       ├── entity_sync.py          # Sincronización de entidades
    │       ├── input_manager.py        # Gestión de inputs
    │       └── prediction.py           # Sistema de predicción
    └── generated/                      # Código gRPC generado
        ├── game_pb2.py
        └── game_pb2_grpc.py
```

### Componentes a Implementar

1. **NetworkingManager**:

   - Gestiona conexión gRPC
   - Maneja errores de red
   - Proporciona interfaz para enviar acciones

2. **ServerProxy**:

   - Representa al servidor localmente
   - Almacena estado actual del juego
   - Reconcilia estado con actualizaciones del servidor

3. **EntitySync**:

   - Sincroniza objetos entre servidor y cliente
   - Crea, actualiza y elimina objetos según mensajes del servidor
   - Mantiene mapeo de IDs del servidor a objetos locales

4. **InputManager**:
   - Captura y envía acciones del usuario
   - Numera secuencialmente los comandos
   - Mantiene historial para reconciliación

### Integración con el Juego Existente

1. **Adaptación de SpaceShooterGame**:

   - Añadir modo de juego en red
   - Distinguir entre objetos locales y remotos
   - Delegar autoridad al servidor

2. **Modificación de Player**:

   - Separar entrada de lógica
   - Añadir interpolación para jugadores remotos
   - Implementar predicción y reconciliación

3. **Modificación de Meteor y Missile**:
   - Añadir soporte para IDs de red
   - Permitir actualización desde eventos del servidor

## Sincronización de Estado

### Autoridad del Servidor

El servidor es la autoridad final sobre:

- Posición y estado de todos los objetos
- Colisiones y daño
- Puntuación y estado del juego

### Predicción del Cliente

Para una experiencia con baja latencia:

1. El cliente predice el resultado de las acciones del jugador local
2. Aplica movimiento inmediatamente
3. Envía la acción al servidor con timestamp y número de secuencia
4. Cuando llega la confirmación del servidor, reconcilia si es necesario

### Interpolación

Para movimiento fluido de objetos remotos:

1. Almacenar posiciones pasadas con timestamp
2. Interpolar entre posiciones conocidas
3. Renderizar posición interpolada en lugar de la más reciente

## Manejo de Eventos

### Eventos del Servidor al Cliente

- **EntityCreate**: Crear nuevo objeto (meteorito, misil, jugador)
- **EntityUpdate**: Actualizar posición/estado de objeto existente
- **EntityDestroy**: Eliminar objeto (meteorito destruido, misil impactado)
- **PlayerJoined/Left**: Notificar cambios en jugadores conectados
- **GameStateChange**: Cambios en estado de juego (inicio, pausa, fin)

### Eventos del Cliente al Servidor

- **PlayerInput**: Acciones del usuario (movimiento, disparo)
- **PlayerReady**: Indicar que el jugador está listo para comenzar
- **Heartbeat**: Mantener conexión activa

## Gestión de Objetos

### Identificadores Únicos

Cada objeto del juego tiene un ID único global:

- Formato UUID para garantizar unicidad
- El servidor asigna IDs al crear objetos
- Los clientes referencian objetos por su ID

### Ciclo de Vida de Objetos

1. **Creación**:

   - Servidor decide crear un objeto (ej: meteorito)
   - Asigna ID único y envía evento EntityCreate
   - Cliente crea objeto local con mismo ID

2. **Actualización**:

   - Servidor calcula nueva posición/estado
   - Envía actualizaciones periódicas
   - Cliente actualiza objeto o interpola

3. **Destrucción**:
   - Servidor decide destruir objeto (colisión, fuera de pantalla)
   - Envía evento EntityDestroy
   - Cliente elimina objeto correspondiente

## Consideraciones de Rendimiento

### Optimización de Tráfico

1. **Actualización incremental**:

   - Enviar solo cambios, no estado completo
   - Priorizar objetos cercanos a jugadores

2. **Compresión de datos**:

   - Usar tipos eficientes (int32 vs strings)
   - Enviar coordenadas con precisión limitada

3. **Frecuencia adaptativa**:
   - Ajustar tasa de actualización según condiciones de red
   - Implementar estrategia de heartbeat para detectar desconexiones

### Sincronización de Hitboxes

1. **Datos estáticos compartidos**:

   - Usar las mismas dimensiones de hitbox en cliente y servidor
   - Precargar configuración de hitboxes desde archivo JSON

2. **Depuración visual**:
   - Permitir visualización de hitboxes del servidor vs cliente
   - Implementar herramientas de depuración de red

## Plan de Implementación

### Fase 1: Infraestructura Básica

1. **Definición del protocolo gRPC**:

   - Ampliar definiciones en game.proto
   - Generar código para cliente y servidor

2. **Implementación del servidor Go**:

   - Estructuras base del motor
   - Servidor gRPC básico
   - Sistema de salas

3. **Adaptación básica del cliente**:
   - Cliente gRPC
   - Integración con menú

### Fase 2: Implementación Core

1. **Migración de la lógica de juego a Go**:

   - Implementar GameEngine
   - Recrear entidades (Player, Meteor, Missile)
   - Sistema de colisiones

2. **Sincronización básica cliente-servidor**:
   - Transmisión de posiciones
   - Creación/eliminación de objetos

### Fase 3: Características Avanzadas

1. **Predicción e interpolación**:

   - Movimiento suave de objetos remotos
   - Predicción de acciones locales

2. **Optimizaciones de red**:

   - Compresión y priorización
   - Manejo de latencia

3. **Características multijugador**:
   - Sistema de puntuación
   - Chat básico (opcional)

### Consideraciones Futuras

1. **Escalabilidad**:

   - Soporte para múltiples salas simultáneas
   - Persistencia de estadísticas

2. **Seguridad**:

   - Validación de inputs
   - Autenticación básica

3. **Manejo de desconexiones**:
   - Reconexión automática
   - Estado de pausa durante desconexiones
