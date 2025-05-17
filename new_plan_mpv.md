# Plan MVV para Multijugador: Space Shooter

## Enfoque Simplificado (client-trust)

Este plan representa una versión mínima viable (MVV) del sistema multijugador para Space Shooter. La diferencia principal con el plan completo es que **confiaremos en los clientes para manejar la lógica del juego**, incluyendo colisiones, daño y puntuación. El servidor actuará principalmente como un retransmisor de eventos entre clientes.

**Nota:** Este enfoque permite posibles trampas, pero simplifica enormemente la implementación inicial y permite un desarrollo más rápido.

## 1. Arquitectura Simplificada

### Distribución de responsabilidades:

1. **Cliente Python:**

   - Procesamiento de entrada del usuario
   - Lógica de juego (movimiento, colisiones, daño)
   - Renderizado
   - Notificación de eventos importantes al servidor

2. **Servidor Go:**
   - Gestión de conexiones de clientes
   - Retransmisión de eventos entre clientes
   - No ejecuta lógica de juego
   - No valida acciones del cliente

### Flujo de comunicación:

1. Cliente A detecta una colisión o evento importante
2. Cliente A notifica al servidor con detalles del evento
3. Servidor retransmite el evento a todos los clientes (incluido Cliente A)
4. Todos los clientes procesan el evento y actualizan su estado local

## 2. Estructura del Proyecto

Mantendremos la misma estructura de carpetas que en el plan original:

```
python-space-shooter/
├── legacy/                    # Código anterior
├── config.json                # Configuración general
├── go-server/                 # Servidor Go simplificado
│   ├── main.go                # Punto de entrada del servidor
│   ├── config/                # Configuración del servidor
│   ├── proto/                 # Definiciones de protobuf y gRPC
│   └── networking/            # Gestión de red simplificada
│       └── server.go          # Servidor gRPC (solo retransmisión)
├── python-game/               # Cliente Python original con modificaciones
    └── src/
        ├── menu/
        ├── motor/
        └── space_shooter/
            ├── networking/    # Nueva carpeta para la red
            │   └── networking_manager.py  # Cliente gRPC
```

## 3. Protocolo de Comunicación (gRPC)

### 3.1 Mensajes principales

El protocolo será más simple, ya que el servidor solo retransmite eventos:

```protobuf
syntax = "proto3";

package spaceshooter;

// Servicio principal del juego
service GameService {
  // Conectar a una sala (crea una si no existe)
  rpc JoinGame(JoinRequest) returns (stream GameEvent);

  // Enviar un evento al servidor para retransmisión
  rpc SendEvent(ClientEvent) returns (EventResponse);
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
}

// Evento del cliente al servidor
message ClientEvent {
  string player_id = 1;
  EventType type = 2;

  // Datos del evento según el tipo
  oneof event_data {
    PlayerPosition player_position = 3;
    MeteorInfo meteor_info = 4;
    MissileInfo missile_info = 5;
    CollisionInfo collision_info = 6;
  }
}

// Evento del servidor al cliente (retransmitido)
message GameEvent {
  string origin_player_id = 1;  // ID del jugador que originó el evento
  EventType type = 2;

  // Mismos datos que ClientEvent
  oneof event_data {
    PlayerPosition player_position = 3;
    MeteorInfo meteor_info = 4;
    MissileInfo missile_info = 5;
    CollisionInfo collision_info = 6;
  }
}

// Respuesta a un evento enviado
message EventResponse {
  bool success = 1;
  string message = 2;
}

// Información de posición de un jugador
message PlayerPosition {
  float x = 1;
  float y = 2;
  float speed_x = 3;
  float speed_y = 4;
  int32 lives = 5;
  int32 score = 6;
}

// Información de un meteorito
message MeteorInfo {
  string meteor_id = 1;
  string meteor_type = 2;
  float x = 3;
  float y = 4;
  float speed_x = 5;
  float speed_y = 6;
  float angle = 7;
  float rotation_speed = 8;
  int32 hp = 9;
}

// Información de un misil
message MissileInfo {
  string missile_id = 1;
  float x = 2;
  float y = 3;
  float speed_y = 4;
}

// Información de una colisión
message CollisionInfo {
  string object1_id = 1;
  string object2_id = 2;
  string object1_type = 3;
  string object2_type = 4;
  float x = 5;
  float y = 6;
}
```

## 4. Implementación del Servidor (Simplificada)

### 4.1 Servidor Go (server.go)

```go
package main

import (
    "log"
    "net"
    "sync"

    "github.com/google/uuid"
    "google.golang.org/grpc"
    pb "github.com/your-username/space-shooter/proto"
)

// GameServer implementa el servicio gRPC
type GameServer struct {
    pb.UnimplementedGameServiceServer

    clientsMutex sync.RWMutex
    clients      map[string]*Client
}

// Client representa un cliente conectado
type Client struct {
    ID        string
    Name      string
    EventChan chan *pb.GameEvent
}

// NewGameServer crea un nuevo servidor de juego
func NewGameServer() *GameServer {
    return &GameServer{
        clients: make(map[string]*Client),
    }
}

// JoinGame implementa la función RPC para unirse al juego
func (s *GameServer) JoinGame(req *pb.JoinRequest, stream pb.GameService_JoinGameServer) error {
    // Generar ID único para el cliente
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

    // Notificar a todos los clientes sobre el nuevo jugador
    joinEvent := &pb.GameEvent{
        OriginPlayerId: clientID,
        Type:           pb.EventType_PLAYER_JOINED,
        EventData: &pb.GameEvent_PlayerPosition{
            PlayerPosition: &pb.PlayerPosition{
                X:      200, // Posición inicial
                Y:      500,
                SpeedX: 0,
                SpeedY: 0,
                Lives:  3,
                Score:  0,
            },
        },
    }
    s.broadcastEvent(joinEvent)

    // Limpiar al desconectar
    defer func() {
        s.clientsMutex.Lock()
        delete(s.clients, clientID)
        s.clientsMutex.Unlock()

        // Notificar desconexión a otros clientes
        leaveEvent := &pb.GameEvent{
            OriginPlayerId: clientID,
            Type:           pb.EventType_PLAYER_LEFT,
        }
        s.broadcastEvent(leaveEvent)

        close(eventChan)
    }()

    // Enviar ID del cliente como primer evento
    initialEvent := &pb.GameEvent{
        OriginPlayerId: "server",
        Type:           pb.EventType_PLAYER_JOINED,
        EventData: &pb.GameEvent_PlayerPosition{
            PlayerPosition: &pb.PlayerPosition{
                X:      200,
                Y:      500,
                SpeedX: 0,
                SpeedY: 0,
                Lives:  3,
                Score:  0,
            },
        },
    }
    if err := stream.Send(initialEvent); err != nil {
        return err
    }

    // Enviar eventos al cliente en streaming
    for event := range eventChan {
        if err := stream.Send(event); err != nil {
            log.Printf("Error enviando evento: %v", err)
            return err
        }
    }

    return nil
}

// SendEvent implementa la función RPC para enviar eventos al servidor
func (s *GameServer) SendEvent(ctx context.Context, event *pb.ClientEvent) (*pb.EventResponse, error) {
    // Verificar que el cliente existe
    s.clientsMutex.RLock()
    _, exists := s.clients[event.PlayerId]
    s.clientsMutex.RUnlock()

    if !exists {
        return &pb.EventResponse{
            Success: false,
            Message: "Cliente no encontrado",
        }, nil
    }

    // Convertir ClientEvent a GameEvent
    gameEvent := &pb.GameEvent{
        OriginPlayerId: event.PlayerId,
        Type:           event.Type,
        EventData:      event.EventData,
    }

    // Retransmitir evento a todos los clientes
    s.broadcastEvent(gameEvent)

    return &pb.EventResponse{
        Success: true,
        Message: "",
    }, nil
}

// broadcastEvent envía un evento a todos los clientes
func (s *GameServer) broadcastEvent(event *pb.GameEvent) {
    s.clientsMutex.RLock()
    defer s.clientsMutex.RUnlock()

    for _, client := range s.clients {
        select {
        case client.EventChan <- event:
            // Evento enviado con éxito
        default:
            // Canal lleno, descartar evento
            log.Printf("Canal de eventos lleno para cliente %s", client.ID)
        }
    }
}

func main() {
    // Iniciar servidor gRPC
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("Error al escuchar: %v", err)
    }

    grpcServer := grpc.NewServer()
    gameServer := NewGameServer()

    // Registrar servicio
    pb.RegisterGameServiceServer(grpcServer, gameServer)

    log.Println("Servidor iniciado en :50051")
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("Error en el servidor: %v", err)
    }
}
```

## 5. Implementación del Cliente Python

### 5.1 NetworkingManager (networking_manager.py)

```python
import grpc
import threading
import pygame
from time import time
from google.protobuf.json_format import MessageToDict
from . import spaceshooter_pb2 as pb
from . import spaceshooter_pb2_grpc as pb_grpc

class NetworkingManager:
    """Gestiona la comunicación con el servidor gRPC."""

    def __init__(self, game):
        self.game = game
        self.channel = None
        self.stub = None
        self.stream_thread = None
        self.running = False
        self.player_id = None
        self.player_name = "Player"  # Nombre por defecto
        self.last_events = {}  # Para evitar enviar eventos duplicados

    def connect(self, server_address="localhost:50051"):
        """Conecta al servidor gRPC."""
        try:
            # Crear canal gRPC
            self.channel = grpc.insecure_channel(server_address)
            self.stub = pb_grpc.GameServiceStub(self.channel)

            # Iniciar thread para recibir eventos
            self.running = True
            self.stream_thread = threading.Thread(target=self._receive_events)
            self.stream_thread.daemon = True
            self.stream_thread.start()

            return True
        except Exception as e:
            print(f"Error conectando al servidor: {e}")
            return False

    def disconnect(self):
        """Desconecta del servidor."""
        self.running = False
        if self.channel:
            self.channel.close()

    def _receive_events(self):
        """Recibe eventos del servidor (en un thread separado)."""
        try:
            # Unirse al juego
            join_request = pb.JoinRequest(player_name=self.player_name)

            # Iniciar stream de eventos del servidor
            for event in self.stub.JoinGame(join_request):
                if not self.running:
                    break

                # Guardar el ID del jugador si es el primer evento
                if event.origin_player_id == "server" and not self.player_id:
                    self.player_id = event.player_position.player_id

                # Procesar evento según su tipo
                self._process_event(event)

        except Exception as e:
            print(f"Error recibiendo eventos: {e}")

    def _process_event(self, event):
        """Procesa un evento recibido del servidor."""
        # Ignorar eventos propios (excepto el inicial)
        if event.origin_player_id == self.player_id and event.origin_player_id != "server":
            return

        # Diferentes acciones según el tipo de evento
        if event.type == pb.EventType.PLAYER_JOINED:
            # Jugador se unió
            pos = event.player_position
            self.game.emit_event("player_joined", {
                "player_id": event.origin_player_id,
                "x": pos.x,
                "y": pos.y,
                "lives": pos.lives,
                "score": pos.score
            })

        elif event.type == pb.EventType.PLAYER_LEFT:
            # Jugador abandonó la partida
            self.game.emit_event("player_left", {
                "player_id": event.origin_player_id
            })

        elif event.type == pb.EventType.PLAYER_MOVED:
            # Jugador se movió
            pos = event.player_position
            self.game.emit_event("player_moved", {
                "player_id": event.origin_player_id,
                "x": pos.x,
                "y": pos.y,
                "speed_x": pos.speed_x,
                "speed_y": pos.speed_y
            })

        elif event.type == pb.EventType.METEOR_CREATED:
            # Crear un nuevo meteorito
            meteor = event.meteor_info
            self.game.emit_event("create_meteor", {
                "meteor_id": meteor.meteor_id,
                "meteor_type": meteor.meteor_type,
                "x": meteor.x,
                "y": meteor.y,
                "speed_x": meteor.speed_x,
                "speed_y": meteor.speed_y,
                "angle": meteor.angle,
                "rotation_speed": meteor.rotation_speed,
                "hp": meteor.hp
            })

        elif event.type == pb.EventType.METEOR_DESTROYED:
            # Meteorito destruido
            meteor = event.meteor_info
            self.game.emit_event("meteor_destroyed", {
                "meteor_id": meteor.meteor_id,
                "x": meteor.x,
                "y": meteor.y
            })

        elif event.type == pb.EventType.MISSILE_FIRED:
            # Jugador disparó un misil
            missile = event.missile_info
            self.game.emit_event("create_missile", {
                "missile_id": missile.missile_id,
                "player_id": event.origin_player_id,
                "x": missile.x,
                "y": missile.y,
                "speed_y": missile.speed_y
            })

        elif event.type == pb.EventType.PLAYER_HIT:
            # Jugador recibió daño
            pos = event.player_position
            self.game.emit_event("player_hit", {
                "player_id": event.origin_player_id,
                "lives": pos.lives
            })

        elif event.type == pb.EventType.PLAYER_DIED:
            # Jugador perdió todas sus vidas
            self.game.emit_event("player_died", {
                "player_id": event.origin_player_id
            })

    def send_event(self, event_type, event_data=None):
        """Envía un evento al servidor."""
        if not self.player_id or not self.stub:
            return False

        # Evitar enviar eventos duplicados en poco tiempo
        current_time = time()
        key = (event_type, str(event_data))
        last_time = self.last_events.get(key, 0)

        # Limitar la frecuencia según el tipo de evento
        min_interval = 0.05  # 50ms por defecto

        if event_type == pb.EventType.PLAYER_MOVED:
            min_interval = 0.1  # 100ms para movimiento

        if current_time - last_time < min_interval:
            return False

        # Registrar tiempo del evento
        self.last_events[key] = current_time

        try:
            # Crear evento según el tipo
            client_event = pb.ClientEvent(
                player_id=self.player_id,
                type=event_type
            )

            # Añadir datos específicos según el tipo
            if event_type == pb.EventType.PLAYER_MOVED:
                client_event.event_data.player_position.CopyFrom(
                    pb.PlayerPosition(
                        x=event_data["x"],
                        y=event_data["y"],
                        speed_x=event_data["speed_x"],
                        speed_y=event_data["speed_y"],
                        lives=event_data.get("lives", 3),
                        score=event_data.get("score", 0)
                    )
                )
            elif event_type == pb.EventType.METEOR_CREATED:
                client_event.event_data.meteor_info.CopyFrom(
                    pb.MeteorInfo(
                        meteor_id=event_data["meteor_id"],
                        meteor_type=event_data["meteor_type"],
                        x=event_data["x"],
                        y=event_data["y"],
                        speed_x=event_data["speed_x"],
                        speed_y=event_data["speed_y"],
                        angle=event_data["angle"],
                        rotation_speed=event_data["rotation_speed"],
                        hp=event_data.get("hp", 1)
                    )
                )
            elif event_type == pb.EventType.MISSILE_FIRED:
                client_event.event_data.missile_info.CopyFrom(
                    pb.MissileInfo(
                        missile_id=event_data["missile_id"],
                        x=event_data["x"],
                        y=event_data["y"],
                        speed_y=event_data.get("speed_y", -500)
                    )
                )

            # Enviar evento al servidor
            response = self.stub.SendEvent(client_event)
            return response.success

        except Exception as e:
            print(f"Error enviando evento: {e}")
            return False

    def notify_player_moved(self, x, y, speed_x, speed_y, lives=None, score=None):
        """Notifica que el jugador se ha movido."""
        data = {
            "x": x,
            "y": y,
            "speed_x": speed_x,
            "speed_y": speed_y
        }
        if lives is not None:
            data["lives"] = lives
        if score is not None:
            data["score"] = score

        return self.send_event(pb.EventType.PLAYER_MOVED, data)

    def notify_meteor_created(self, meteor):
        """Notifica que se ha creado un meteorito."""
        data = {
            "meteor_id": meteor.id,
            "meteor_type": meteor.meteor_type,
            "x": meteor.x,
            "y": meteor.y,
            "speed_x": meteor.speed_x,
            "speed_y": meteor.speed_y,
            "angle": meteor.angle,
            "rotation_speed": meteor.rotation_speed,
            "hp": meteor.hp if hasattr(meteor, "hp") else 1
        }
        return self.send_event(pb.EventType.METEOR_CREATED, data)

    def notify_meteor_destroyed(self, meteor):
        """Notifica que se ha destruido un meteorito."""
        data = {
            "meteor_id": meteor.id,
            "x": meteor.x,
            "y": meteor.y
        }
        return self.send_event(pb.EventType.METEOR_DESTROYED, data)

    def notify_missile_fired(self, missile):
        """Notifica que se ha disparado un misil."""
        data = {
            "missile_id": missile.id,
            "x": missile.x,
            "y": missile.y,
            "speed_y": missile.speed_y
        }
        return self.send_event(pb.EventType.MISSILE_FIRED, data)

    def notify_player_hit(self, lives):
        """Notifica que el jugador ha recibido daño."""
        data = {
            "lives": lives
        }
        return self.send_event(pb.EventType.PLAYER_HIT, data)

    def notify_player_died(self):
        """Notifica que el jugador ha muerto."""
        return self.send_event(pb.EventType.PLAYER_DIED)
```

### 5.2 Modificaciones al SpaceShooterGame

```python
# Modificaciones necesarias al SpaceShooterGame

# Método para crear ID únicos
def generate_id(self, prefix="obj"):
    """Genera un ID único para objetos del juego."""
    import uuid
    return f"{prefix}_{str(uuid.uuid4())[:8]}"

# Modificar la creación de meteoritos para asignar IDs
def create_meteor(self, meteor_type, position, speed, rotation):
    # Crear meteorito normalmente
    meteor = super().create_meteor(meteor_type, position, speed, rotation)

    # Asignar ID único
    meteor.id = self.generate_id("meteor")

    # Si estamos en modo multijugador y somos el host, notificar
    if self.is_multiplayer and self.is_host:
        self.networking.notify_meteor_created(meteor)

    return meteor

# Modificar la creación de misiles para asignar IDs
def player_fire_missile(self, player_id, x, y):
    # Crear misil normalmente
    missile = super().player_fire_missile(player_id, x, y)

    # Asignar ID único
    missile.id = self.generate_id("missile")

    # Si estamos en modo multijugador, notificar
    if self.is_multiplayer:
        self.networking.notify_missile_fired(missile)

    return missile

# Modificar la detección de colisiones para notificar
def handle_collision(self, obj1, obj2):
    # Manejar colisión normalmente
    result = super().handle_collision(obj1, obj2)

    # Si estamos en modo multijugador y ocurrió una colisión importante
    if self.is_multiplayer and result:
        # Si un meteorito fue destruido
        if obj1.type == "meteor" and obj1.hp <= 0:
            self.networking.notify_meteor_destroyed(obj1)
        elif obj2.type == "meteor" and obj2.hp <= 0:
            self.networking.notify_meteor_destroyed(obj2)

        # Si el jugador recibió daño
        if obj1.type == "player" and obj1.player_id == self.networking.player_id:
            self.networking.notify_player_hit(obj1.lives)
            if obj1.lives <= 0:
                self.networking.notify_player_died()
        elif obj2.type == "player" and obj2.player_id == self.networking.player_id:
            self.networking.notify_player_hit(obj2.lives)
            if obj2.lives <= 0:
                self.networking.notify_player_died()

    return result

# Actualizar posición del jugador regularmente
def update(self):
    # Actualización normal
    super().update()

    # Si estamos en modo multijugador, enviar posición del jugador periódicamente
    if self.is_multiplayer and self.player:
        # Solo enviar si ha pasado suficiente tiempo (100ms)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_position_update > 100:
            self.networking.notify_player_moved(
                self.player.x,
                self.player.y,
                self.player.speed_x,
                self.player.speed_y,
                self.player.lives,
                self.player.score
            )
            self.last_position_update = current_time
```

### 5.3 Objetos para Representación de Entidades Remotas

Para manejar correctamente las entidades que pertenecen a otros jugadores, se han creado dos nuevas clases:

#### 5.3.1 OtherPlayer

Esta clase representa a un jugador remoto controlado por otro cliente.

```python
# other_player.py
class OtherPlayer(GameObject):
    """Clase que representa a otros jugadores en el juego Space Shooter multijugador."""

    def __init__(self, x, y, player_id, player_name):
        # Inicialización con ID y nombre de red
        super().__init__(x, y, None, "other_player")
        self.player_id = player_id
        self.player_name = player_name
        # ... configuración similar a Player

    def on_collide(self, other_entity):
        """
        IMPORTANTE: No reacciona a colisiones con meteoritos,
        ya que eso lo maneja el cliente original.
        """
        # No hacer nada, el jugador original maneja sus colisiones
        return False

    def simulate_damage(self):
        """
        Simula el efecto visual de recibir daño, sin enviar eventos al servidor.
        """
        # ... activar frames de invencibilidad y parpadeo

    def update_position(self, x, y, speed_x, speed_y):
        """Actualiza la posición según datos recibidos del servidor."""
        # ... actualizar posición y velocidad
```

**Características clave:**

- Controlado únicamente por eventos recibidos del servidor
- No responde a eventos de teclado
- Al colisionar con meteoritos, no envía eventos de daño al servidor
- Solo muestra visualmente los efectos de daño cuando recibe notificación
- Mantiene su propio estado de vidas y puntuación para mostrarlo

#### 5.3.2 OtherMissile

Esta clase representa un misil disparado por otro jugador.

```python
# other_missile.py
class OtherMissile(GameObject):
    """Clase que representa los misiles disparados por otros jugadores."""

    def __init__(self, x, y, missile_id, player_id):
        # Inicialización con IDs de red
        super().__init__(x, y, None, obj_type="other_missile")
        self.id = missile_id
        self.player_id = player_id
        # ... configuración similar a Missile

    def on_collide(self, other_entity):
        """
        IMPORTANTE: No causa daño real, solo visual.
        """
        if other_entity.type == "meteor" and not self.has_hit:
            self.has_hit = True
            self.should_destroy = True

            # No aplica daño real al meteorito, solo efecto visual
            # El dueño original del misil enviará el evento de daño

            return True
        return False

    def get_damage(self):
        """Obtiene el daño que causa este misil (solo visual)."""
        return 0  # No causa daño real
```

**Características clave:**

- Se mueve hacia arriba como un misil normal
- Se destruye al impactar con un meteorito (visualmente)
- Al impactar, NO CAUSA DAÑO REAL al meteorito
- El meteorito mostrará visualmente el efecto de daño pero no perderá HP
- El cliente original que disparó el misil es el único que envía la señal de daño

### 5.3.3 Nota Importante sobre Colisiones

**IMPORTANTE: Prevención de Duplicación de Eventos**

Para evitar que múltiples clientes envíen los mismos eventos de colisión al servidor, se establece la siguiente regla:

1. **Colisiones de jugador-meteorito**: Solo el cliente que controla al jugador envía el evento de daño al servidor cuando su nave colisiona con un meteorito. Los demás clientes solo muestran el efecto visual cuando reciben la notificación del servidor.

2. **Colisiones de misil-meteorito**: Solo el cliente que disparó el misil envía el evento de daño al servidor cuando su misil impacta con un meteorito. Los demás clientes muestran el efecto visual pero no aplican daño al meteorito ni envían eventos adicionales.

Esta estrategia evita:

- Sobrecarga de eventos duplicados en el servidor
- Aplicación duplicada de daño a entidades
- Inconsistencias entre el estado de los clientes

Los objetos `OtherPlayer` y `OtherMissile` están diseñados específicamente para implementar este comportamiento, representando visualmente las acciones pero sin generar eventos adicionales.

## 6. Plan de Implementación

### Fase 1: Preparación

1. Crear estructura de carpetas para el servidor Go
2. Definir mensajes protobuf para comunicación gRPC
3. Generar código cliente/servidor a partir de los protobuf

### Fase 2: Implementación del Servidor Simple

4. Implementar servidor gRPC básico en Go
5. Implementar sistema de retransmisión de eventos

### Fase 3: Modificaciones al Cliente Python

6. Implementar NetworkingManager para comunicación con servidor
7. Modificar SpaceShooterGame para asignar IDs a objetos
8. Añadir sistema de notificación de eventos
9. Adaptar manejo de colisiones para enviar notificaciones

### Fase 4: Pruebas

10. Probar conexión de múltiples clientes
11. Probar sincronización de jugadores y meteoritos
12. Probar colisiones y eventos del juego

## 7. Ventajas de este Enfoque

1. **Simplicidad**: El servidor es mucho más simple, no requiere replicar la lógica del juego
2. **Reutilización**: El código existente en Python apenas requiere modificaciones
3. **Desarrollo rápido**: Permite tener un prototipo multijugador funcional rápidamente
4. **Depuración más sencilla**: Al mantener la lógica en Python, facilita la depuración

## 8. Limitaciones y Consideraciones

1. **Seguridad limitada**: Los clientes pueden enviar eventos fraudulentos (trampas)
2. **Sincronización imperfecta**: Puede haber discrepancias entre los estados de diferentes clientes
3. **Latencia**: Los eventos deben viajar cliente → servidor → otros clientes
4. **Escalabilidad**: Este enfoque es adecuado para pocos jugadores (2-4)

## 9. Siguientes Pasos

1. Implementar la estructura básica del servidor Go con modelo de retransmisión
2. Adaptar el cliente Python para asignar IDs y notificar eventos
3. Probar con múltiples clientes
4. Evaluar rendimiento y comportamiento para mejoras futuras

## 10. Notas Finales

Este plan MVV permite implementar rápidamente un prototipo multijugador funcional que puede servir como base para un sistema más robusto en el futuro. Una vez que el prototipo esté funcionando, se puede evaluar qué aspectos de la autoridad del servidor son más críticos para implementar en una fase posterior.
