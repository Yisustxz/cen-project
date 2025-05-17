# Plan de Implementación: Sistema Multijugador Space Shooter

## 1. Resumen

Implementaremos un sistema multijugador para el juego Space Shooter que actualmente funciona en modo local. El servidor será desarrollado en Go y utilizará gRPC para la comunicación con los clientes Python. El sistema permitirá que múltiples jugadores se conecten a una sala de juego para jugar en modo cooperativo o competitivo.

**_Nota: Este plan se ha dividido en tres partes debido a su extensión:_**

- **_multplayer_task_pending.md (Parte 1): Estructura general y componentes principales_**
- **_multplayer_task_pending_part2.md (Parte 2): Detalles de implementación_**
- **_multplayer_task_pending_part3.md (Parte 3): Flujos de comunicación y etapas de desarrollo_**

## 2. Estructura del Proyecto

### 2.1 Organización de Carpetas

Reorganizaremos el proyecto con la siguiente estructura:

```
python-space-shooter/
├── legacy/                    # Código anterior (frontend, proto, backend/server)
├── config.json                # Configuración general
├── go-server/                 # Nuevo servidor Go
│   ├── main.go                # Punto de entrada del servidor
│   ├── config/                # Configuración del servidor
│   ├── proto/                 # Definiciones de protobuf y gRPC
│   ├── motor/                 # Motor del juego en Go (equivalente a motor/ en Python)
│   │   ├── game_engine.go
│   │   ├── objects_manager.go
│   │   └── sprite.go
│   ├── utils/                 # Utilidades
│   │   └── delta_time.go
│   └── space_shooter/         # Lógica específica del juego Space Shooter
│       ├── core/              # Componentes principales del juego
│       │   ├── game.go        # Gestión de una sala de juego
│       │   ├── meteor_manager.go
│       │   └── constants.go
│       ├── entities/          # Entidades del juego
│       │   ├── player.go
│       │   ├── meteor.go
│       │   └── missile.go
│       ├── data/              # Datos estáticos
│       │   └── meteor_data.go
│       └── networking/        # Gestión de red
│           └── server.go      # Servidor gRPC
├── python-game/               # Cliente Python original con modificaciones
    └── src/
        ├── menu/
        ├── motor/
        └── space_shooter/
            ├── networking/    # Nueva carpeta para la red
            │   └── networking_manager.py  # Cliente gRPC
```

## 3. Componentes del Sistema

### 3.1 Servidor Go

#### 3.1.1 Motor del Juego (motor/)

- **game_engine.go**: Implementación del bucle de juego y gestión básica
- **objects_manager.go**: Gestión de objetos del juego y colisiones
- **sprite.go**: Equivalente a GameObject para representar entidades

#### 3.1.2 Utilidades (utils/)

- **delta_time.go**: Sistema de tiempo delta para mantener velocidades consistentes

#### 3.1.3 Módulo Space Shooter (space_shooter/)

- **core/game.go**: Gestión de una sala de juego
- **core/meteor_manager.go**: Gestión de meteoritos
- **core/constants.go**: Constantes del juego
- **entities/**: Implementaciones de las entidades (player, meteor, missile)
- **data/meteor_data.go**: Definición de tipos y propiedades de meteoritos

#### 3.1.4 Sistema de Red (networking/)

- **server.go**: Implementación del servidor gRPC

### 3.2 Modificaciones al Cliente Python

- **networking_manager.py**: Cliente gRPC para comunicación con el servidor
- Modificaciones al menú para eliminar la opción "Crear" y solo mostrar "Unirse"
- Ajustes en las clases del juego para recibir eventos del servidor

## 4. Protocolo de Comunicación (gRPC)

### 4.1 Mensajes principales

```protobuf
syntax = "proto3";

package spaceshooter;

// Servicio principal del juego
service GameService {
  // Conectar a una sala (crea una si no existe)
  rpc JoinGame(JoinRequest) returns (stream GameEvent);

  // Enviar acción del jugador al servidor
  rpc SendPlayerAction(PlayerAction) returns (ActionResponse);
}

// Solicitud para unirse a una sala
message JoinRequest {
  string player_name = 1;
}

// Tipos de eventos del juego
enum EventType {
  PLAYER_JOINED = 0;
  PLAYER_LEFT = 1;
  METEOR_CREATED = 2;
  METEOR_DESTROYED = 3;
  MISSILE_FIRED = 4;
  PLAYER_HIT = 5;
  PLAYER_DIED = 6;
  GAME_OVER = 7;
  GAME_STATE = 8;
}

// Evento del juego (servidor -> cliente)
message GameEvent {
  EventType type = 1;

  // Datos específicos según el tipo de evento
  oneof event_data {
    PlayerInfo player_info = 2;
    MeteorInfo meteor_info = 3;
    MissileInfo missile_info = 4;
    GameState game_state = 5;
  }
}

// Acción del jugador (cliente -> servidor)
message PlayerAction {
  string player_id = 1;

  // Tipo de acción
  enum ActionType {
    MOVE_LEFT = 0;
    MOVE_RIGHT = 1;
    STOP = 2;
    FIRE = 3;
  }
  ActionType action = 2;
}

// Respuesta a una acción del jugador
message ActionResponse {
  bool success = 1;
  string message = 2;
}

// Información de un jugador
message PlayerInfo {
  string player_id = 1;
  string name = 2;
  float position_x = 3;
  float position_y = 4;
  int32 lives = 5;
  int32 score = 6;
}

// Información de un meteorito
message MeteorInfo {
  string meteor_id = 1;
  string meteor_type = 2;
  float position_x = 3;
  float position_y = 4;
  float speed_x = 5;
  float speed_y = 6;
  float angle = 7;
  float rotation_speed = 8;
  int32 image_index = 9;  // Para elegir entre diferentes imágenes del mismo tipo
}

// Información de un misil
message MissileInfo {
  string missile_id = 1;
  string player_id = 2;  // Jugador que disparó
  float position_x = 3;
  float position_y = 4;
}

// Estado completo del juego (para sincronización)
message GameState {
  repeated PlayerInfo players = 1;
  repeated MeteorInfo meteors = 2;
  repeated MissileInfo missiles = 3;
}
```

## 5. Implementación del Servidor Go

### 5.1 Estructura Base (main.go)

```go
package main

import (
    "log"
    "net"
    "google.golang.org/grpc"
    "github.com/your-username/space-shooter/go-server/networking"
)

func main() {
    // Cargar configuración

    // Iniciar servidor gRPC
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("Error al escuchar: %v", err)
    }

    grpcServer := grpc.NewServer()
    gameServer := networking.NewGameServer()

    // Registrar servicio
    spaceshooter.RegisterGameServiceServer(grpcServer, gameServer)

    log.Println("Servidor iniciado en :50051")
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("Error en el servidor: %v", err)
    }
}
```

### 5.2 Motor del Juego (game_engine.go)

```go
package motor

import (
    "time"
    "github.com/your-username/space-shooter/go-server/utils"
)

// GameEngine representa el motor del juego
type GameEngine struct {
    Running       bool
    ObjectsManager *ObjectsManager
    DeltaTime     *utils.DeltaTime
    // Otros campos necesarios
}

// NewGameEngine crea una nueva instancia del motor
func NewGameEngine() *GameEngine {
    engine := &GameEngine{
        Running:       false,
        ObjectsManager: NewObjectsManager(),
        DeltaTime:     utils.NewDeltaTime(),
    }
    return engine
}

// Start inicia el bucle del juego
func (engine *GameEngine) Start() {
    engine.Running = true
    go engine.gameLoop()
}

// Stop detiene el bucle del juego
func (engine *GameEngine) Stop() {
    engine.Running = false
}

// gameLoop es el bucle principal del juego
func (engine *GameEngine) gameLoop() {
    // Inicializar deltaTime
    engine.DeltaTime.Init()

    for engine.Running {
        // Actualizar deltaTime
        engine.DeltaTime.Update()

        // Actualizar objetos
        engine.Update()

        // Dormir para mantener un ritmo razonable en el servidor
        time.Sleep(16 * time.Millisecond) // ~60 fps
    }
}

// Update actualiza la lógica del juego
func (engine *GameEngine) Update() {
    // Actualizar todos los objetos
    engine.ObjectsManager.UpdateObjects()

    // Detectar colisiones
    engine.ObjectsManager.DetectCollisions()

    // Limpiar objetos destruidos
    engine.ObjectsManager.CleanDestroyedObjects()
}

// RegisterObject registra un objeto en el motor
func (engine *GameEngine) RegisterObject(obj *Sprite) {
    engine.ObjectsManager.RegisterObject(obj)
}

// UnregisterObject elimina un objeto del motor
func (engine *GameEngine) UnregisterObject(obj *Sprite) {
    engine.ObjectsManager.UnregisterObject(obj)
}
```

## 6. Implementación del Networking en Python

### 6.1 Cliente gRPC (networking_manager.py)

```python
"""
Gestor de red para la comunicación con el servidor Go.
"""
import threading
import grpc
import spaceshooter_pb2
import spaceshooter_pb2_grpc

class NetworkingManager:
    """
    Clase para manejar la comunicación con el servidor.
    """

    def __init__(self, game):
        """
        Inicializa el gestor de red.

        Args:
            game: Referencia al juego principal
        """
        self.game = game
        self.channel = None
        self.stub = None
        self.player_id = None
        self.connected = False
        self.event_thread = None

    def connect(self, server_address, player_name):
        """
        Conecta al servidor.

        Args:
            server_address: Dirección del servidor
            player_name: Nombre del jugador

        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            # Crear canal gRPC
            self.channel = grpc.insecure_channel(server_address)
            self.stub = spaceshooter_pb2_grpc.GameServiceStub(self.channel)

            # Crear solicitud de unión
            join_request = spaceshooter_pb2.JoinRequest(player_name=player_name)

            # Iniciar stream de eventos
            self.event_stream = self.stub.JoinGame(join_request)

            # Iniciar hilo para recibir eventos
            self.event_thread = threading.Thread(target=self._process_events)
            self.event_thread.daemon = True
            self.event_thread.start()

            self.connected = True
            return True
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False

    def disconnect(self):
        """Desconecta del servidor."""
        self.connected = False
        if self.channel:
            self.channel.close()

    def _process_events(self):
        """Procesa eventos recibidos del servidor."""
        try:
            for event in self.event_stream:
                self._handle_event(event)
        except Exception as e:
            print(f"Error en el stream de eventos: {e}")
            self.connected = False

    def _handle_event(self, event):
        """
        Maneja un evento recibido del servidor.

        Args:
            event: Evento recibido
        """
        # Determinar tipo de evento
        if event.type == spaceshooter_pb2.EventType.PLAYER_JOINED:
            # Manejar nuevo jugador
            player_info = event.player_info
            if not self.player_id:
                self.player_id = player_info.player_id
            # Notificar al juego

        elif event.type == spaceshooter_pb2.EventType.METEOR_CREATED:
            # Crear meteorito localmente
            meteor_info = event.meteor_info
            self.game.meteor_manager.create_meteor_from_network(
                meteor_type=meteor_info.meteor_type,
                position=(meteor_info.position_x, meteor_info.position_y),
                speed=(meteor_info.speed_x, meteor_info.speed_y),
                rotation=(meteor_info.angle, meteor_info.rotation_speed),
                image_index=meteor_info.image_index
            )

        # Manejar otros tipos de eventos...

    def send_player_action(self, action_type):
        """
        Envía una acción del jugador al servidor.

        Args:
            action_type: Tipo de acción

        Returns:
            bool: True si la acción se envió correctamente
        """
        if not self.connected or not self.player_id:
            return False

        try:
            action = spaceshooter_pb2.PlayerAction(
                player_id=self.player_id,
                action=action_type
            )
            response = self.stub.SendPlayerAction(action)
            return response.success
        except Exception as e:
            print(f"Error al enviar acción: {e}")
            return False
```

## 7. Plan de Implementación

### Fase 1: Preparación y Estructura

1. Crear estructura de carpetas para servidor Go
2. Definir mensajes protobuf para comunicación gRPC
3. Generar código cliente/servidor a partir de los protobuf
4. Implementar estructuras básicas del motor en Go

### Fase 2: Implementación del Servidor

5. Implementar DeltaTime en Go
6. Implementar GameEngine, ObjectsManager y Sprite
7. Implementar entidades básicas (Player, Meteor, Missile)
8. Implementar MeteorManager y lógica del juego
9. Implementar servidor gRPC y gestión de salas

### Fase 3: Modificaciones al Cliente Python

10. Reestructurar menú para mostrar solo "Unirse"
11. Implementar NetworkingManager para comunicación con servidor
12. Modificar MeteorManager para recibir datos del servidor
13. Modificar Player para enviar acciones al servidor
14. Implementar sincronización de estado del juego

### Fase 4: Pruebas y Refinamiento

15. Pruebas de conexión cliente-servidor
16. Pruebas de multijugador básico
17. Implementar gestión de latencia
18. Optimizaciones y mejoras de rendimiento

## 8. Consideraciones y Retos

1. **Sincronización de estado**: Manejar las diferencias entre lo que ve cada jugador.
2. **Latencia**: Implementar técnicas para hacer el juego responsivo pese a la latencia de red.
3. **Autoridad del servidor**: El servidor debe ser la autoridad final para evitar trampas.
4. **Escalabilidad**: Diseñar para manejar múltiples salas simultáneas si es necesario.
5. **Recuperación de errores**: Manejar desconexiones y problemas de red.

## 9. Próximos Pasos

1. Aprobar este plan
2. Implementar la estructura básica del servidor Go
3. Definir los protobuf para la comunicación
4. Implementar el motor del juego en Go

# Continuación del Plan de Implementación

## 10. Detalles de Implementación

### 10.1 Implementación del Delta Time en Go (utils/delta_time.go)

```go
package utils

import (
    "sync"
    "time"
)

// DeltaTime mantiene el tiempo entre frames para actualizar
// movimientos independientes de la velocidad del juego
type DeltaTime struct {
    lastTime  time.Time
    delta     float64
    maxDelta  float64
    baseFPS   float64
    mutex     sync.Mutex
}

// NewDeltaTime crea una nueva instancia de DeltaTime
func NewDeltaTime() *DeltaTime {
    return &DeltaTime{
        maxDelta: 0.2,  // 200ms máximo para evitar saltos grandes
        baseFPS:  60.0,
    }
}

// Init inicializa el sistema de tiempo delta
func (dt *DeltaTime) Init() {
    dt.mutex.Lock()
    defer dt.mutex.Unlock()

    dt.lastTime = time.Now()
    dt.delta = 0
}

// Update actualiza el delta time basado en el tiempo desde el último frame
func (dt *DeltaTime) Update() {
    dt.mutex.Lock()
    defer dt.mutex.Unlock()

    currentTime := time.Now()
    elapsed := currentTime.Sub(dt.lastTime).Seconds()

    // Limitar el delta máximo para evitar saltos grandes
    if elapsed > dt.maxDelta {
        elapsed = dt.maxDelta
    }

    dt.delta = elapsed
    dt.lastTime = currentTime
}

// GetDelta obtiene el tiempo delta entre frames en segundos
func (dt *DeltaTime) GetDelta() float64 {
    dt.mutex.Lock()
    defer dt.mutex.Unlock()

    return dt.delta
}

// GetFixedDelta obtiene el tiempo delta fijo basado en los FPS base
func (dt *DeltaTime) GetFixedDelta() float64 {
    return 1.0 / dt.baseFPS
}

// GetScaleFactor obtiene el factor de escala para ajustar valores
func (dt *DeltaTime) GetScaleFactor() float64 {
    dt.mutex.Lock()
    defer dt.mutex.Unlock()

    fixedDelta := dt.GetFixedDelta()
    if fixedDelta == 0 {
        return 1.0
    }
    return dt.delta / fixedDelta
}

// ScaleValue escala un valor basado en el delta time actual
func (dt *DeltaTime) ScaleValue(value float64) float64 {
    dt.mutex.Lock()
    defer dt.mutex.Unlock()

    return value * dt.delta
}

// ScaleValuePerSecond convierte un valor por segundo en un valor
// por frame según el delta time
func (dt *DeltaTime) ScaleValuePerSecond(valuePerSecond float64) float64 {
    dt.mutex.Lock()
    defer dt.mutex.Unlock()

    return valuePerSecond * dt.delta
}
```

### 10.2 Implementación de Sprite en Go (motor/sprite.go)

```go
package motor

import (
    "math"
    "github.com/your-username/space-shooter/go-server/utils"
)

// Vector2D representa un vector bidimensional
type Vector2D struct {
    X float64
    Y float64
}

// Sprite es la clase base para todos los objetos del juego
type Sprite struct {
    Position      Vector2D
    Velocity      Vector2D
    Width         int
    Height        int
    Type          string
    ID            string
    Angle         float64
    RotationSpeed float64
    HasHitbox     bool
    Hitbox        struct {
        Width  int
        Height int
        X      int
        Y      int
    }
    Game          *GameEngine
    IsVisible     bool
    IsDestroyed   bool
}

// NewSprite crea un nuevo sprite
func NewSprite(x, y float64, width, height int, objType string) *Sprite {
    return &Sprite{
        Position: Vector2D{X: x, Y: y},
        Velocity: Vector2D{X: 0, Y: 0},
        Width:    width,
        Height:   height,
        Type:     objType,
        HasHitbox: true,
        IsVisible: true,
        Hitbox: struct {
            Width  int
            Height int
            X      int
            Y      int
        }{
            Width:  width,
            Height: height,
            X:      int(x) - width/2,
            Y:      int(y) - height/2,
        },
    }
}

// SetGame establece la referencia al juego principal
func (s *Sprite) SetGame(game *GameEngine) {
    s.Game = game
}

// SetVelocity establece la velocidad del objeto en ambos ejes
func (s *Sprite) SetVelocity(speedX, speedY float64) {
    s.Velocity.X = speedX
    s.Velocity.Y = speedY
}

// SetRotation establece el ángulo y velocidad de rotación
func (s *Sprite) SetRotation(angle, speed float64) {
    s.Angle = angle
    s.RotationSpeed = speed
}

// CreateHitbox crea o actualiza la hitbox basada en las dimensiones
func (s *Sprite) CreateHitbox(padding int) {
    if !s.HasHitbox {
        return
    }

    width := s.Width + padding*2
    height := s.Height + padding*2

    // Asegurar dimensiones mínimas
    if width < 1 {
        width = 1
    }
    if height < 1 {
        height = 1
    }

    s.Hitbox.Width = width
    s.Hitbox.Height = height
    s.UpdateHitboxPosition()
}

// UpdateHitboxPosition actualiza la posición de la hitbox
func (s *Sprite) UpdateHitboxPosition() {
    if !s.HasHitbox {
        return
    }

    s.Hitbox.X = int(s.Position.X) - s.Hitbox.Width/2
    s.Hitbox.Y = int(s.Position.Y) - s.Hitbox.Height/2
}

// Update actualiza el sprite según el tiempo delta
func (s *Sprite) Update(deltaTime *utils.DeltaTime) {
    // Aplicar velocidad usando delta time
    delta := deltaTime.GetDelta()

    if s.Velocity.X != 0 {
        s.Position.X += s.Velocity.X * delta
    }
    if s.Velocity.Y != 0 {
        s.Position.Y += s.Velocity.Y * delta
    }

    // Actualizar hitbox
    s.UpdateHitboxPosition()

    // Actualizar rotación si hay velocidad de rotación
    if s.RotationSpeed != 0 {
        s.Angle += s.RotationSpeed * delta
        // Mantener ángulo entre 0-360
        s.Angle = math.Mod(s.Angle, 360)
        if s.Angle < 0 {
            s.Angle += 360
        }
    }

    // Llamar al método específico del objeto
    s.OnUpdate()
}

// OnUpdate es llamado por Update, para ser sobrescrito por los objetos específicos
func (s *Sprite) OnUpdate() {
    // Este método debe ser implementado por las clases derivadas
}

// CollidesWith verifica si este sprite colisiona con otro
func (s *Sprite) CollidesWith(other *Sprite) bool {
    if !s.HasHitbox || !other.HasHitbox {
        return false
    }

    // Comprobar si las hitboxes se solapan
    return !(s.Hitbox.X > other.Hitbox.X + other.Hitbox.Width ||
             s.Hitbox.X + s.Hitbox.Width < other.Hitbox.X ||
             s.Hitbox.Y > other.Hitbox.Y + other.Hitbox.Height ||
             s.Hitbox.Y + s.Hitbox.Height < other.Hitbox.Y)
}

// OnCollide maneja la colisión con otro sprite
func (s *Sprite) OnCollide(other *Sprite) bool {
    // Este método debe ser implementado por las clases derivadas
    return false
}

// Destroy marca el objeto para ser eliminado
func (s *Sprite) Destroy() {
    s.IsDestroyed = true
}
```

### 10.3 Implementación del ObjectsManager en Go (motor/objects_manager.go)

```go
package motor

import (
    "sync"
)

// ObjectsManager gestiona todos los objetos del juego
type ObjectsManager struct {
    objects         []*Sprite
    objectsByType   map[string][]*Sprite
    objectsToAdd    []*Sprite
    objectsToRemove []*Sprite
    mutex           sync.RWMutex
}

// NewObjectsManager crea un nuevo gestor de objetos
func NewObjectsManager() *ObjectsManager {
    return &ObjectsManager{
        objects:       make([]*Sprite, 0),
        objectsByType: make(map[string][]*Sprite),
        objectsToAdd:  make([]*Sprite, 0),
        objectsToRemove: make([]*Sprite, 0),
    }
}

// RegisterObject añade un objeto al gestor
func (om *ObjectsManager) RegisterObject(obj *Sprite) {
    om.mutex.Lock()
    om.objectsToAdd = append(om.objectsToAdd, obj)
    om.mutex.Unlock()
}

// UnregisterObject marca un objeto para ser eliminado
func (om *ObjectsManager) UnregisterObject(obj *Sprite) {
    om.mutex.Lock()
    om.objectsToRemove = append(om.objectsToRemove, obj)
    om.mutex.Unlock()
}

// UpdateObjects actualiza todos los objetos registrados
func (om *ObjectsManager) UpdateObjects() {
    // Procesar objetos pendientes de añadir/eliminar
    om.processObjectChanges()

    // Actualizar objetos existentes
    om.mutex.RLock()
    for _, obj := range om.objects {
        if obj.Game != nil && !obj.IsDestroyed {
            obj.Update(obj.Game.DeltaTime)
        }
    }
    om.mutex.RUnlock()
}

// processObjectChanges añade o elimina objetos pendientes
func (om *ObjectsManager) processObjectChanges() {
    om.mutex.Lock()
    defer om.mutex.Unlock()

    // Añadir nuevos objetos
    if len(om.objectsToAdd) > 0 {
        for _, obj := range om.objectsToAdd {
            om.objects = append(om.objects, obj)

            // Añadir a la colección por tipo
            objType := obj.Type
            if _, exists := om.objectsByType[objType]; !exists {
                om.objectsByType[objType] = make([]*Sprite, 0)
            }
            om.objectsByType[objType] = append(om.objectsByType[objType], obj)
        }
        om.objectsToAdd = om.objectsToAdd[:0] // Limpiar lista
    }

    // Eliminar objetos marcados
    if len(om.objectsToRemove) > 0 {
        for _, objToRemove := range om.objectsToRemove {
            // Eliminar de la lista principal
            for i, obj := range om.objects {
                if obj == objToRemove {
                    // Reemplazar con el último elemento y reducir slice
                    lastIndex := len(om.objects) - 1
                    om.objects[i] = om.objects[lastIndex]
                    om.objects = om.objects[:lastIndex]
                    break
                }
            }

            // Eliminar de la colección por tipo
            objType := objToRemove.Type
            if typeList, exists := om.objectsByType[objType]; exists {
                for i, obj := range typeList {
                    if obj == objToRemove {
                        lastIndex := len(typeList) - 1
                        typeList[i] = typeList[lastIndex]
                        om.objectsByType[objType] = typeList[:lastIndex]
                        break
                    }
                }
            }
        }
        om.objectsToRemove = om.objectsToRemove[:0] // Limpiar lista
    }
}

// DetectCollisions detecta y maneja colisiones entre objetos
func (om *ObjectsManager) DetectCollisions() {
    om.mutex.RLock()
    defer om.mutex.RUnlock()

    // Estrategia simple de detección de colisiones O(n²)
    // En una implementación real, se utilizaría un algoritmo más eficiente
    objectCount := len(om.objects)
    for i := 0; i < objectCount-1; i++ {
        obj1 := om.objects[i]
        if obj1.IsDestroyed || !obj1.HasHitbox {
            continue
        }

        for j := i + 1; j < objectCount; j++ {
            obj2 := om.objects[j]
            if obj2.IsDestroyed || !obj2.HasHitbox {
                continue
            }

            // Verificar colisión
            if obj1.CollidesWith(obj2) {
                // Notificar a ambos objetos
                obj1.OnCollide(obj2)
                obj2.OnCollide(obj1)
            }
        }
    }
}

// GetObjectsByType obtiene objetos de un tipo específico
func (om *ObjectsManager) GetObjectsByType(objType string) []*Sprite {
    om.mutex.RLock()
    defer om.mutex.RUnlock()

    if objects, exists := om.objectsByType[objType]; exists {
        return objects
    }
    return make([]*Sprite, 0)
}

// CountObjectsByType cuenta objetos de un tipo específico
func (om *ObjectsManager) CountObjectsByType(objType string) int {
    om.mutex.RLock()
    defer om.mutex.RUnlock()

    if objects, exists := om.objectsByType[objType]; exists {
        return len(objects)
    }
    return 0
}

// CleanDestroyedObjects elimina objetos marcados para destrucción
func (om *ObjectsManager) CleanDestroyedObjects() {
    om.mutex.RLock()
    for _, obj := range om.objects {
        if obj.IsDestroyed {
            om.mutex.RUnlock()
            om.UnregisterObject(obj)
            om.mutex.RLock()
        }
    }
    om.mutex.RUnlock()
}

// ClearObjects elimina todos los objetos
func (om *ObjectsManager) ClearObjects() {
    om.mutex.Lock()
    defer om.mutex.Unlock()

    om.objects = make([]*Sprite, 0)
    om.objectsByType = make(map[string][]*Sprite)
    om.objectsToAdd = make([]*Sprite, 0)
    om.objectsToRemove = make([]*Sprite, 0)
}
```

### 10.4 Modificaciones al Meteor Manager Python

```python
"""
Modificaciones al gestor de meteoritos para integrarse con el servidor.
"""

def create_meteor_from_network(self, meteor_type, position, speed, rotation, image_index=0):
    """
    Crea un meteorito basado en datos recibidos del servidor.

    Args:
        meteor_type: Tipo de meteorito (ej: 'grey_small')
        position: Tupla (x, y) con la posición inicial
        speed: Tupla (speed_x, speed_y) con la velocidad
        rotation: Tupla (angle, speed) con el ángulo y velocidad de rotación
        image_index: Índice de la imagen a usar (para tipos con múltiples imágenes)

    Returns:
        Meteor: El meteorito creado, o None si hubo un error
    """
    try:
        # Obtener datos para el tipo de meteorito
        meteor_data = MeteorData.get_type_data(meteor_type)

        # Cargar imagen del meteorito según el índice
        meteor_img = MeteorData.load_meteor_image(
            self.resource_manager,
            meteor_type,
            image_index
        )

        # Crear el meteorito con los datos recibidos de la red
        meteor = Meteor(
            meteor_img,
            meteor_type,
            meteor_data,
            position,
            speed,
            rotation
        )

        # Registrar el meteorito en el motor
        self.game.register_object(meteor)

        print(f"Meteorito tipo {meteor_type} creado desde la red.")
        return meteor
    except Exception as e:
        print(f"Error al crear meteorito desde la red: {e}")
        import traceback
        traceback.print_exc()
        return None
```

### 10.5 Implementación del Servidor Game en Go (networking/server.go)

```go
package networking

import (
    "context"
    "log"
    "sync"
    "github.com/google/uuid"
    "github.com/your-username/space-shooter/go-server/motor"
    "github.com/your-username/space-shooter/go-server/space_shooter/core"
    pb "github.com/your-username/space-shooter/go-server/proto"
)

// GameServer implementa el servicio gRPC
type GameServer struct {
    pb.UnimplementedGameServiceServer

    roomsMutex sync.RWMutex
    rooms      map[string]*core.GameRoom
    activeRoom string

    clientsMutex sync.RWMutex
    clients      map[string]*Client
}

// Client representa un cliente conectado
type Client struct {
    ID        string
    Name      string
    RoomID    string
    EventChan chan *pb.GameEvent
}

// NewGameServer crea un nuevo servidor de juego
func NewGameServer() *GameServer {
    server := &GameServer{
        rooms:   make(map[string]*core.GameRoom),
        clients: make(map[string]*Client),
    }
    return server
}

// JoinGame implementa la función RPC para unirse a una sala
func (s *GameServer) JoinGame(req *pb.JoinRequest, stream pb.GameService_JoinGameServer) error {
    // Crear ID único para el cliente
    clientID := uuid.New().String()

    // Crear canal de eventos para este cliente
    eventChan := make(chan *pb.GameEvent, 100)

    // Registrar cliente
    client := &Client{
        ID:        clientID,
        Name:      req.PlayerName,
        EventChan: eventChan,
    }

    s.clientsMutex.Lock()
    s.clients[clientID] = client
    s.clientsMutex.Unlock()

    defer func() {
        // Limpiar al desconectar
        s.clientsMutex.Lock()
        delete(s.clients, clientID)
        s.clientsMutex.Unlock()

        // Notificar desconexión a la sala
        if client.RoomID != "" {
            s.roomsMutex.RLock()
            room, exists := s.rooms[client.RoomID]
            s.roomsMutex.RUnlock()

            if exists {
                room.RemovePlayer(clientID)
                s.broadcastPlayerLeft(client.RoomID, clientID)
            }
        }

        close(eventChan)
    }()

    // Unir jugador a una sala (crear si no existe)
    roomID := s.joinOrCreateRoom(clientID, req.PlayerName)
    client.RoomID = roomID

    // Enviar estado actual del juego al nuevo jugador
    s.sendGameState(roomID, clientID)

    // Notificar a otros jugadores
    s.broadcastPlayerJoined(roomID, clientID, req.PlayerName)

    // Enviar eventos al cliente en streaming
    for event := range eventChan {
        if err := stream.Send(event); err != nil {
            log.Printf("Error enviando evento: %v", err)
            return err
        }
    }

    return nil
}

// SendPlayerAction implementa la función RPC para enviar acciones del jugador
func (s *GameServer) SendPlayerAction(ctx context.Context, action *pb.PlayerAction) (*pb.ActionResponse, error) {
    // Obtener cliente
    s.clientsMutex.RLock()
    client, exists := s.clients[action.PlayerId]
    s.clientsMutex.RUnlock()

    if !exists {
        return &pb.ActionResponse{
            Success: false,
            Message: "Jugador no encontrado",
        }, nil
    }

    // Obtener sala
    s.roomsMutex.RLock()
    room, roomExists := s.rooms[client.RoomID]
    s.roomsMutex.RUnlock()

    if !roomExists {
        return &pb.ActionResponse{
            Success: false,
            Message: "Sala no encontrada",
        }, nil
    }

    // Procesar acción del jugador
    success := room.HandlePlayerAction(action.PlayerId, int(action.Action))

    return &pb.ActionResponse{
        Success: success,
        Message: "",
    }, nil
}

// joinOrCreateRoom une a un jugador a una sala existente o crea una nueva
func (s *GameServer) joinOrCreateRoom(playerID, playerName string) string {
    s.roomsMutex.Lock()
    defer s.roomsMutex.Unlock()

    // Si ya hay una sala activa, unir al jugador a esa sala
    if s.activeRoom != "" {
        room, exists := s.rooms[s.activeRoom]
        if exists && room.IsActive() {
            room.AddPlayer(playerID, playerName)
            return s.activeRoom
        }
    }

    // Crear nueva sala
    roomID := uuid.New().String()
    newRoom := core.NewGameRoom(roomID)
    newRoom.AddPlayer(playerID, playerName)
    newRoom.SetEventCallback(s.handleGameEvent)

    // Iniciar sala
    newRoom.Start()

    // Guardar sala
    s.rooms[roomID] = newRoom
    s.activeRoom = roomID

    log.Printf("Sala creada: %s", roomID)
    return roomID
}

// handleGameEvent maneja eventos generados por el juego
func (s *GameServer) handleGameEvent(roomID string, eventType int, data interface{}) {
    // Crear evento según el tipo
    var event *pb.GameEvent

    switch eventType {
    case core.EventMeteorCreated:
        if meteorData, ok := data.(*core.MeteorData); ok {
            event = &pb.GameEvent{
                Type: pb.EventType_METEOR_CREATED,
                EventData: &pb.GameEvent_MeteorInfo{
                    MeteorInfo: &pb.MeteorInfo{
                        MeteorId:      meteorData.ID,
                        MeteorType:    meteorData.Type,
                        PositionX:     float32(meteorData.X),
                        PositionY:     float32(meteorData.Y),
                        SpeedX:        float32(meteorData.SpeedX),
                        SpeedY:        float32(meteorData.SpeedY),
                        Angle:         float32(meteorData.Angle),
                        RotationSpeed: float32(meteorData.RotationSpeed),
                        ImageIndex:    int32(meteorData.ImageIndex),
                    },
                },
            }
        }

    // Manejar otros tipos de eventos...
    }

    // Enviar evento a todos los clientes de la sala
    if event != nil {
        s.broadcastEvent(roomID, event)
    }
}

// broadcastEvent envía un evento a todos los clientes en una sala
func (s *GameServer) broadcastEvent(roomID string, event *pb.GameEvent) {
    s.clientsMutex.RLock()
    defer s.clientsMutex.RUnlock()

    for _, client := range s.clients {
        if client.RoomID == roomID {
            select {
            case client.EventChan <- event:
                // Evento enviado con éxito
            default:
                // Canal lleno, descartar evento
                log.Printf("Canal de eventos lleno para cliente %s", client.ID)
            }
        }
    }
}

// Otras funciones de utilidad para la comunicación...
```

## 11. Resumen de Tareas Pendientes

### 11.1 Servidor Go

1. **Base del proyecto:**

   - Estructura de carpetas y archivos
   - Configuración básica y sistema de logging

2. **Motor del juego:**

   - Implementación de DeltaTime
   - Implementación de GameEngine
   - Implementación de ObjectsManager
   - Implementación de Sprite

3. **Módulo Space Shooter:**

   - Implementación de GameRoom
   - Implementación de MeteorManager
   - Implementación de Player
   - Implementación de Meteor
   - Implementación de Missile

4. **Networking:**
   - Definición de protobuf
   - Generación de código gRPC
   - Implementación del servidor gRPC
   - Gestión de clientes y salas

### 11.2 Cliente Python

1. **Adaptaciones del menú:**

   - Eliminar opción "Crear"
   - Modificar flujo para solo "Unirse"

2. **Networking:**

   - Crear carpeta networking
   - Implementar NetworkingManager
   - Integrar protocolo gRPC

3. **Adaptaciones del juego:**

   - Modificar MeteorManager para recibir datos del servidor
   - Modificar Player para enviar acciones al servidor
   - Adaptar el sistema de colisiones

4. **Sincronización:**
   - Implementar estado del juego
   - Manejar joining a partida en curso

# Implementación de Multijugador: Parte 3

## 12. Flujo de Comunicación

Para entender mejor el flujo de comunicación entre el cliente y el servidor, aquí presentamos una serie de diagramas de secuencia de las operaciones más importantes:

### 12.1 Flujo de Unión a Partida

1. **Cliente** solicita unirse a una partida
2. **Servidor** verifica si existe una sala activa
   - Si no existe: crea una nueva sala y la inicia
   - Si existe: añade el jugador a la sala existente
3. **Servidor** envía el estado actual del juego al cliente
4. **Servidor** notifica a otros jugadores sobre el nuevo jugador
5. **Cliente** recibe el estado actual y crea todos los objetos necesarios
6. Se establece la conexión de streaming para eventos continuos

### 12.2 Flujo de Generación de Meteoritos

1. **Servidor** determina que es momento de crear un meteorito
2. **Servidor** genera propiedades aleatorias para el meteorito
3. **Servidor** crea el meteorito en su motor de juego
4. **Servidor** envía evento `METEOR_CREATED` a todos los clientes
5. **Cliente** recibe el evento y crea un meteorito idéntico localmente

### 12.3 Flujo de Control del Jugador

1. **Cliente** detecta que el usuario presiona una tecla
2. **Cliente** envía acción `MOVE_LEFT`, `MOVE_RIGHT` o `STOP` al servidor
3. **Servidor** actualiza la posición del jugador en su motor
4. **Servidor** envía evento `PLAYER_MOVED` a todos los clientes
5. **Cliente** recibe el evento y actualiza la posición de ese jugador

### 12.4 Flujo de Disparo

1. **Cliente** detecta que el usuario presiona la tecla de disparo
2. **Cliente** envía acción `FIRE` al servidor
3. **Servidor** verifica si el jugador puede disparar (cooldown)
4. **Servidor** crea el misil en su motor de juego
5. **Servidor** envía evento `MISSILE_FIRED` a todos los clientes
6. **Cliente** recibe el evento y crea un misil idéntico localmente

### 12.5 Flujo de Colisiones

1. **Servidor** detecta colisión entre un misil y un meteorito
2. **Servidor** aplica daño al meteorito
3. **Servidor** verifica si el meteorito fue destruido
4. Si fue destruido:
   - **Servidor** envía evento `METEOR_DESTROYED` a todos los clientes
   - **Servidor** actualiza puntuación del jugador
   - **Servidor** envía evento `SCORE_UPDATED` a todos los clientes
5. **Cliente** recibe eventos y actualiza su estado local

## 13. Implementación de la Estructura Inicial

### 13.1 Creación de Carpetas y Estructura Base

```
mkdir -p go-server/proto
mkdir -p go-server/config
mkdir -p go-server/motor
mkdir -p go-server/utils
mkdir -p go-server/space_shooter/core
mkdir -p go-server/space_shooter/entities
mkdir -p go-server/space_shooter/data
mkdir -p go-server/space_shooter/networking
```

### 13.2 Definición del Protocolo gRPC

Primero, necesitamos crear el archivo .proto que definirá la comunicación entre cliente y servidor:

```proto
// go-server/proto/spaceshooter.proto
syntax = "proto3";

package spaceshooter;

option go_package = "github.com/your-username/space-shooter/proto";

// Servicio principal del juego
service GameService {
  // Conectar a una sala (crea una si no existe)
  rpc JoinGame(JoinRequest) returns (stream GameEvent);

  // Enviar acción del jugador al servidor
  rpc SendPlayerAction(PlayerAction) returns (ActionResponse);
}

// Solicitud para unirse a una sala
message JoinRequest {
  string player_name = 1;
}

// Tipos de eventos del juego
enum EventType {
  PLAYER_JOINED = 0;
  PLAYER_LEFT = 1;
  METEOR_CREATED = 2;
  METEOR_DESTROYED = 3;
  MISSILE_FIRED = 4;
  PLAYER_HIT = 5;
  PLAYER_DIED = 6;
  PLAYER_MOVED = 7;
  GAME_OVER = 8;
  GAME_STATE = 9;
  SCORE_UPDATED = 10;
}

// Evento del juego (servidor -> cliente)
message GameEvent {
  EventType type = 1;

  // Datos específicos según el tipo de evento
  oneof event_data {
    PlayerInfo player_info = 2;
    MeteorInfo meteor_info = 3;
    MissileInfo missile_info = 4;
    GameState game_state = 5;
    ScoreInfo score_info = 6;
  }
}

// Acción del jugador (cliente -> servidor)
message PlayerAction {
  string player_id = 1;

  // Tipo de acción
  enum ActionType {
    MOVE_LEFT = 0;
    MOVE_RIGHT = 1;
    STOP = 2;
    FIRE = 3;
  }
  ActionType action = 2;
}

// Respuesta a una acción del jugador
message ActionResponse {
  bool success = 1;
  string message = 2;
}

// Información de un jugador
message PlayerInfo {
  string player_id = 1;
  string name = 2;
  float position_x = 3;
  float position_y = 4;
  int32 lives = 5;
  int32 score = 6;
}

// Información de un meteorito
message MeteorInfo {
  string meteor_id = 1;
  string meteor_type = 2;
  float position_x = 3;
  float position_y = 4;
  float speed_x = 5;
  float speed_y = 6;
  float angle = 7;
  float rotation_speed = 8;
  int32 image_index = 9;
  int32 hp = 10;
}

// Información de un misil
message MissileInfo {
  string missile_id = 1;
  string player_id = 2;  // Jugador que disparó
  float position_x = 3;
  float position_y = 4;
}

// Información de puntuación
message ScoreInfo {
  string player_id = 1;
  int32 score = 2;
  int32 points_earned = 3;  // Puntos ganados en este evento
}

// Estado completo del juego (para sincronización)
message GameState {
  repeated PlayerInfo players = 1;
  repeated MeteorInfo meteors = 2;
  repeated MissileInfo missiles = 3;
}
```

### 13.3 Modificaciones al Menú Python

Eliminar la opción "Crear partida" y modificar el menú para mostrar solo "Unirse a partida":

```python
# python-game/src/menu/menu.py (modificado)

class MenuOption(Enum):
    JOIN_GAME = 0  # Ahora es la primera opción
    EXIT = 1       # Ahora es la segunda opción

class MainMenu:
    def __init__(self, screen):
        # ...

        # Opciones del menú actualizadas
        self.options = [
            "Unirse a partida",
            "Salir"
        ]

        # ...

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                # Devolver la opción seleccionada
                if self.selected_option == 0:
                    return MenuOption.JOIN_GAME
                elif self.selected_option == 1:
                    return MenuOption.EXIT

        return None
```

## 14. Dependencias de Go

Para el desarrollo del servidor en Go, necesitaremos las siguientes bibliotecas:

```
go get google.golang.org/grpc
go get google.golang.org/protobuf
go get github.com/google/uuid
go get github.com/spf13/viper  # Para gestión de configuración
```

## 15. Secuencia de Desarrollo Recomendada

Para implementar este sistema de manera efectiva, se recomienda seguir estos pasos en orden:

1. Configurar el entorno de desarrollo (Go y Python)
2. Crear la estructura de carpetas
3. Definir e implementar el protocolo gRPC
4. Implementar el motor básico en Go
   - Implementar DeltaTime
   - Implementar Sprite
   - Implementar ObjectsManager
   - Implementar GameEngine
5. Implementar el sistema básico de red en Go
   - Servidor gRPC
   - Gestión de salas
6. Implementar entidades básicas en Go
   - Player
   - Meteor
   - Missile
7. Implementar la lógica del juego en Go
   - GameRoom
   - MeteorManager
8. Modificar el cliente Python
   - Modificar el menú
   - Implementar NetworkingManager
   - Adaptar los componentes para recibir eventos de red
9. Pruebas y depuración
   - Pruebas de conexión cliente-servidor
   - Pruebas de funcionamiento del juego multijugador
10. Optimizaciones y mejoras

## 16. Consideraciones de Seguridad y Rendimiento

1. **Validación de datos**: Validar todos los datos recibidos del cliente antes de procesarlos
2. **Autoridad del servidor**: El servidor debe ser la autoridad final para prevenir trampas
3. **Control de latencia**: Implementar técnicas como predicción de movimiento si es necesario
4. **Gestión de desconexiones**: Manejar correctamente las desconexiones repentinas
5. **Escalabilidad**: Diseñar el servidor para poder manejar múltiples salas si es necesario
6. **Optimización de mensajes**: Evitar enviar más datos de los necesarios

## 17. Conclusión

El sistema multijugador propuesto permitirá a los jugadores disfrutar del juego Space Shooter en modo cooperativo o competitivo, manteniendo una experiencia de juego fluida y sincronizada. La arquitectura cliente-servidor con Go y gRPC proporciona una base sólida y eficiente para la comunicación en tiempo real.

La implementación seguirá un enfoque incremental, comenzando por las componentes más básicas y añadiendo funcionalidad gradualmente hasta lograr un sistema multijugador completo y funcional.

Una vez que estos componentes estén implementados, el sistema podrá expandirse para incluir funcionalidades adicionales como tablas de clasificación, personalización de naves, o modos de juego adicionales.

## 18. Siguiente Paso Actualizado

Obtener aprobación para este plan de implementación ampliado y comenzar con la creación de la estructura básica del proyecto, teniendo en cuenta las consideraciones adicionales detalladas.

## 19. Consideraciones Adicionales Importantes

### 19.1 Sistema de IDs para Objetos del Juego

Para garantizar la sincronización correcta entre el servidor y los clientes, cada objeto (jugador, meteorito, misil) debe tener un ID único que permita su identificación y seguimiento. Este sistema funcionará de la siguiente manera:

- Cada objeto del juego (Sprite) tendrá un campo `object_id` o `sprite_id`
- La generación de IDs debe ser coordinada entre el cliente y el servidor
- Opciones para implementación:
  - **Opción 1 (Recomendada)**: El servidor genera todos los IDs y los envía al cliente
  - **Opción 2**: Para objetos creados por el cliente (como misiles), el cliente puede generar un ID inicial y enviarlo al servidor junto con el evento de creación
  - **Opción 3**: Depender completamente de los IDs generados por el servidor

Desde el servidor, se utilizará un sistema de generación de IDs similar a UUID pero numérico, que será más eficiente para la serialización y transmisión a través de la red.

Implementación en el cliente:

```python
# Modificación en sprite.py para soportar IDs
def __init__(self, ...):
    # Código existente...
    self.object_id = None  # Será asignado al registrar el objeto o desde la red

def set_object_id(self, object_id):
    self.object_id = object_id
```

### 19.2 Métodos de Creación de Objetos desde la Red

Similar a `create_meteor_from_network`, necesitamos implementar métodos para crear otros tipos de objetos a partir de datos recibidos de la red:

- **create_player_from_network**: Para crear jugadores remotos
- **create_missile_from_network**: Para crear misiles disparados por otros jugadores

Este enfoque permitirá mantener un modelo coherente para la creación de objetos a partir de eventos de red.

```python
# En la clase Player o su gestor
def create_player_from_network(player_id, name, position, ...):
    player = Player(...)
    player.set_object_id(player_id)
    # Configurar otras propiedades
    return player

# En la clase encargada de gestionar misiles
def create_missile_from_network(missile_id, player_id, position, ...):
    missile = Missile(...)
    missile.set_object_id(missile_id)
    # Configurar otras propiedades
    return missile
```

### 19.3 Configuración Inicial y Datos del Jugador

Para simplificar el desarrollo inicial, se obtendrán varios datos de configuración del archivo `config.json`:

- **Nombre del jugador**: Inicialmente se leerá del archivo de configuración
- **Datos de conexión al servidor**: Dirección IP y puerto
- **Otros parámetros de red**: Timeouts, frecuencia de actualización, etc.

Ejemplo de configuración a añadir:

```json
{
  "player": {
    "name": "Player1"
  },
  "network": {
    "server_address": "localhost:50051",
    "timeout_ms": 5000,
    "update_rate_hz": 30
  }
}
```

### 19.4 Desafío de las Hitboxes y Solución Propuesta

Existe un desafío significativo en el manejo de hitboxes:

- **En el cliente Python**: Las hitboxes se calculan actualmente basadas en las imágenes cargadas
- **En el servidor Go**: No hay acceso a las imágenes, por lo que no se pueden calcular de la misma manera

#### Solución propuesta:

1. Modificar el sistema actual para definir hitboxes manualmente
2. Para cada tipo de objeto, especificar:
   - Centro (x, y) de la imagen
   - Dimensiones de la hitbox (ancho, alto)
   - Desplazamiento de la hitbox respecto al centro (offset_x, offset_y)

#### Plan de implementación:

1. Registrar en logs los datos actuales de hitboxes para todos los tipos de meteoros
2. Crear un conjunto de datos estático con las hitboxes predefinidas:

```python
METEOR_HITBOXES = {
    "grey_big": {"width": 96, "height": 96, "center_x": 48, "center_y": 48},
    "grey_medium": {"width": 64, "height": 64, "center_x": 32, "center_y": 32},
    # Otros tipos...
}
```

3. Modificar el sistema de generación de hitboxes para utilizar estos datos predefinidos
4. Implementar el mismo sistema en el servidor Go

Este enfoque permitirá que tanto el cliente como el servidor calculen las hitboxes de manera idéntica, garantizando coherencia en la detección de colisiones.

## 20. Siguiente Paso Actualizado

Obtener aprobación para este plan de implementación ampliado y comenzar con la creación de la estructura básica del proyecto, teniendo en cuenta las consideraciones adicionales detalladas.
