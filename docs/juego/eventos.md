# Sistema de Eventos

El sistema de eventos en Space Shooter permite la comunicación desacoplada entre diferentes componentes del juego, facilitando la notificación de acciones importantes y permitiendo que múltiples objetos reaccionen a un mismo evento.

## Visión General

Space Shooter implementa un sistema de eventos personalizado que permite:

- **Comunicación desacoplada**: Los objetos pueden comunicarse sin conocerse directamente
- **Reducción de dependencias**: Minimiza el acoplamiento entre componentes
- **Propagación de información**: Distribuye notificaciones a múltiples receptores
- **Centralización de lógica**: Facilita la gestión de comportamientos complejos
- **Extensibilidad**: Permite añadir nuevos tipos de eventos sin modificar el código existente

## Arquitectura del Sistema

```
+------------------+      +------------------+
|   GameEngine     |      |  EventManager    |
+------------------+      +------------------+
|                  |----->| register_listener() |
|                  |      | emit_event()     |
|                  |      | handle_events()  |
+------------------+      +------------------+
         ▲                        |
         |                        |
         |                        v
+------------------+      +------------------+
|    GameObject    |      |   EventListener  |
+------------------+      +------------------+
| emit_event()     |----->| on_game_event()  |
+------------------+      +------------------+
         ▲                        ▲
         |                        |
         |                        |
+------------------+              |
|  Player, Meteor, |--------------|
|  Missile, etc.   |
+------------------+
```

## Tipos de Eventos

Space Shooter define los siguientes tipos de eventos principales:

| Evento                | Descripción                   | Datos                                                   |
| --------------------- | ----------------------------- | ------------------------------------------------------- |
| `player_fire_missile` | El jugador dispara un misil   | `{"x": posX, "y": posY, "type": tipo_misil}`            |
| `player_damage`       | El jugador recibe daño        | `{"remaining_lives": vidas}`                            |
| `meteor_destroyed`    | Un meteorito es destruido     | `{"position": (x, y), "size": tamaño, "score": puntos}` |
| `powerup_collected`   | El jugador recoge un power-up | `{"type": tipo, "position": (x, y)}`                    |
| `game_over`           | El juego ha terminado         | `{"score": puntuación}`                                 |
| `game_paused`         | El juego se ha pausado        | `{}`                                                    |
| `game_resumed`        | El juego se ha reanudado      | `{}`                                                    |
| `level_completed`     | Se ha completado un nivel     | `{"level": nivel, "score": puntuación}`                 |

## Implementación en el Motor

### En GameEngine

```python
def __init__(self, width=800, height=600, title="Game", fps=60):
    # Inicialización del motor
    pygame.init()

    # Creación del administrador de eventos
    self.event_manager = EventManager()

    # Resto de la inicialización...

def handle_events(self):
    """Procesa los eventos del sistema y del juego"""
    # Procesar eventos de Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_p:
                self.toggle_pause()
            elif event.key == pygame.K_d:
                self.toggle_debug()

        # Propagar eventos de Pygame a los objetos
        self.objects_manager.propagate_pygame_event(event)

    # Procesar eventos del juego
    self.event_manager.process_events()
```

### EventManager

```python
class EventManager:
    """Gestiona el sistema de eventos del juego"""

    def __init__(self):
        # Listeners registrados por tipo de evento
        self.listeners = {}
        # Cola de eventos pendientes
        self.event_queue = []

    def register_listener(self, event_type, listener):
        """Registra un objeto para recibir notificaciones de un tipo de evento"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        if listener not in self.listeners[event_type]:
            self.listeners[event_type].append(listener)

    def unregister_listener(self, event_type, listener):
        """Elimina un objeto de la lista de receptores de un tipo de evento"""
        if event_type in self.listeners and listener in self.listeners[event_type]:
            self.listeners[event_type].remove(listener)

    def emit_event(self, event_type, data=None):
        """Añade un evento a la cola para ser procesado en el siguiente ciclo"""
        self.event_queue.append((event_type, data))

    def process_events(self):
        """Procesa todos los eventos pendientes en la cola"""
        # Copiar la cola actual y limpiarla para evitar problemas si se generan nuevos eventos durante el procesamiento
        current_events = self.event_queue.copy()
        self.event_queue.clear()

        # Procesar cada evento
        for event_type, data in current_events:
            # Notificar a todos los listeners registrados para este tipo de evento
            if event_type in self.listeners:
                for listener in self.listeners[event_type]:
                    if hasattr(listener, 'on_game_event'):
                        listener.on_game_event(event_type, data)
```

### GameObject (Clase Base)

```python
class GameObject:
    """Clase base para todos los objetos del juego"""

    def __init__(self):
        # Referencia al motor del juego (se establece al registrar el objeto)
        self.game_engine = None
        # Resto de la inicialización...

    def emit_event(self, event_type, data=None):
        """Emite un evento al sistema de eventos del juego"""
        if self.game_engine and hasattr(self.game_engine, 'event_manager'):
            self.game_engine.event_manager.emit_event(event_type, data)

    def on_game_event(self, event_type, data=None):
        """Recibe notificaciones de eventos del juego"""
        # Implementación por defecto, las subclases deben sobrescribir este método
        pass
```

## Registro de Listeners

Los objetos se registran automáticamente para recibir eventos al ser añadidos al juego:

```python
# En GameEngine
def register_object(self, game_object):
    """Registra un objeto en el juego"""
    # Añadir al administrador de objetos
    self.objects_manager.register_object(game_object)

    # Establecer referencia al motor
    game_object.game_engine = self

    # Registrar como listener para todos los eventos, si implementa on_game_event
    if hasattr(game_object, 'on_game_event'):
        # El objeto escuchará todos los eventos por defecto
        for event_type in GAME_EVENT_TYPES:
            self.event_manager.register_listener(event_type, game_object)
```

## Ejemplo: Emisión de Eventos

### Disparo de Misil

```python
# En la clase Player
def fire_missile(self):
    """Intenta disparar un misil"""
    current_time = pygame.time.get_ticks()

    # Verificar cooldown
    if current_time - self.last_missile > self.missile_cooldown:
        self.last_missile = current_time

        # Emitir evento de disparo
        self.emit_event("player_fire_missile", {
            "x": self.rect.centerx,
            "y": self.rect.top,
            "type": "enhanced" if self.rapid_fire > 0 else "normal"
        })

        # Reproducir sonido
        self.play_sound("laser")
```

### Destrucción de Meteorito

```python
# En la clase Meteor
def explode(self):
    """Inicia la explosión del meteorito"""
    # Activar animación
    self.explosion_active = True
    self.explosion_frame = 0

    # Desactivar colisiones durante la explosión
    self.collidable = False

    # Emitir evento
    self.emit_event("meteor_destroyed", {
        "position": (self.rect.centerx, self.rect.centery),
        "size": self.size,
        "score": self.score_value
    })

    # Reproducir sonido
    self.play_sound("explosion")
```

## Ejemplo: Manejo de Eventos

### Creación de Misil

```python
# En la clase SpaceShooterGame
def on_game_event(self, event_type, data=None):
    """Maneja eventos del juego"""

    if event_type == "player_fire_missile":
        # Extraer datos
        x = data.get("x", 0)
        y = data.get("y", 0)
        missile_type = data.get("type", "normal")

        # Crear misil
        self.create_missile(x, y, self.player, missile_type)

    elif event_type == "meteor_destroyed":
        # Manejar destrucción de meteorito
        self.handle_meteor_destroyed(data)

    # Otros manejadores de eventos...
```

### Actualización del HUD

```python
# En la clase HUD
def on_game_event(self, event_type, data=None):
    """Maneja eventos del juego relevantes para el HUD"""

    if event_type == "powerup_collected":
        powerup_type = data.get("type", "") if data else ""

        # Mostrar mensaje según tipo
        if powerup_type == "shield":
            self.show_message("¡Escudo activado!", color=(0, 200, 255))
        elif powerup_type == "rapid_fire":
            self.show_message("¡Disparo rápido!", color=(255, 0, 255))
        elif powerup_type == "extra_life":
            self.show_message("¡Vida extra!", color=(0, 255, 0))
        elif powerup_type == "speed":
            self.show_message("¡Velocidad aumentada!", color=(255, 255, 0))

    elif event_type == "player_damage":
        # Mostrar efecto de daño
        self.show_message("¡Impacto!", color=(255, 0, 0))

    elif event_type == "game_over":
        # Mostrar pantalla de game over
        score = data.get("score", 0) if data else 0
        self.show_game_over(score)
```

## Filtrado de Eventos

Para optimizar el rendimiento, los objetos pueden implementar filtros para procesar solo los eventos relevantes:

```python
# En una clase específica (ej: Meteor)
def on_game_event(self, event_type, data=None):
    """Filtra y maneja solo eventos relevantes"""

    # Solo procesar eventos relevantes para meteoritos
    if event_type == "game_paused":
        self.paused = True
    elif event_type == "game_resumed":
        self.paused = False
    elif event_type == "player_damage" and self.size == "large":
        # Los meteoritos grandes reaccionan al daño del jugador
        # Ejemplo: aumentar velocidad
        self.speed *= 1.2
```

## Eventos Específicos de Contexto

Algunos eventos solo son relevantes en contextos específicos:

```python
# Evento específico para power-ups
if self.shield_remaining > 0 and shield_hit:
    # Emitir evento específico cuando el escudo bloquea un impacto
    self.emit_event("shield_impact", {
        "shield_remaining": self.shield_remaining,
        "position": (self.rect.centerx, self.rect.centery)
    })
```

## Comunicación con el Sistema de Audio

El sistema de eventos también se utiliza para disparar efectos de sonido:

```python
# En AudioManager
def on_game_event(self, event_type, data=None):
    """Reproduce sonidos basados en eventos del juego"""

    if event_type == "player_fire_missile":
        self.play_sound("laser")
    elif event_type == "meteor_destroyed":
        size = data.get("size", "medium") if data else "medium"
        self.play_sound(f"explosion_{size}")
    elif event_type == "powerup_collected":
        powerup_type = data.get("type", "") if data else ""
        self.play_sound(f"powerup_{powerup_type}")
    elif event_type == "player_damage":
        self.play_sound("player_hit")
    elif event_type == "game_over":
        self.play_sound("game_over")
```

## Diagrama de Flujo de Eventos

```
   [Evento generado]
         |
         v
+------------------+
|   EventManager   |
|   emit_event()   |
+------------------+
         |
         v
+------------------+
| Añadir a la cola |
+------------------+
         |
         v
+------------------+
| En el siguiente  |
| ciclo de juego   |
+------------------+
         |
         v
+------------------+
| process_events() |
+------------------+
         |
         v
+------------------+
| Por cada listener|<------+
| registrado       |       |
+------------------+       |
         |                 |
         v                 |
+------------------+       |
| on_game_event()  |       |
+------------------+       |
         |                 |
         v                 |
+------------------+       |
| ¿Más listeners?  |---Sí--+
+------------------+
         |
         No
         v
+------------------+
| Evento procesado |
+------------------+
```

## Buenas Prácticas

1. **Nombres descriptivos**: Usar nombres claros para los tipos de eventos
2. **Datos mínimos**: Incluir solo los datos necesarios en los eventos
3. **Filtrado eficiente**: Implementar filtros para procesar solo eventos relevantes
4. **Evitar ciclos**: Tener cuidado con emisiones de eventos recursivas
5. **Desacoplamiento**: No asumir el orden de procesamiento de los listeners
6. **Documentación clara**: Documentar cada tipo de evento y sus datos
7. **Eliminar listeners**: Desregistrar listeners cuando los objetos se destruyen
