# PowerUp

La clase `PowerUp` representa objetos coleccionables que aparecen durante el juego Space Shooter y otorgan mejoras temporales o permanentes al jugador cuando los recoge.

## Responsabilidades Principales

- **Movimiento descendente** con oscilación lateral
- **Efectos visuales** distintivos según el tipo
- **Comportamiento al ser recogido** (mejora al jugador)
- **Gestión de duración de vida** (desaparición automática)
- **Colisión con el jugador** para activar efectos
- **Variedad de tipos** (escudo, disparo rápido, vida extra, etc.)

## Diagrama de Clase

```
+-------------------+
|     GameObject    |
+-------------------+
         ▲
         │
         │ hereda de
         │
+-------------------+
|      PowerUp      |
+-------------------+
| - type            |
| - speed           |
| - oscillation     |
| - lifetime        |
| - flash_timer     |
| - start_time      |
| ...               |
+-------------------+
| + apply_effect()  |
| + on_update()     |
| + on_collide()    |
| ...               |
+-------------------+
```

## Atributos Principales

| Atributo      | Tipo  | Descripción                                                      |
| ------------- | ----- | ---------------------------------------------------------------- |
| `type`        | str   | Tipo de power-up ('shield', 'rapid_fire', 'extra_life', 'speed') |
| `speed`       | float | Velocidad de caída                                               |
| `oscillation` | dict  | Parámetros para el movimiento de oscilación lateral              |
| `lifetime`    | int   | Tiempo de vida en milisegundos                                   |
| `flash_timer` | int   | Contador para efecto de parpadeo                                 |
| `start_time`  | int   | Timestamp de creación                                            |
| `is_flashing` | bool  | Indica si está parpadeando (próximo a desaparecer)               |

## Inicialización

```python
def __init__(self, x, y, powerup_type='random')
```

**Propósito**: Inicializar un power-up con posición y tipo.

**Parámetros**:

- `x`: Posición X inicial
- `y`: Posición Y inicial
- `powerup_type`: Tipo de power-up o 'random' para selección aleatoria

**Operaciones**:

- Llamar al constructor de la clase padre
- Seleccionar un tipo aleatorio si se especifica 'random'
- Inicializar velocidad, oscilación y otros atributos
- Configurar tiempo de vida y efectos visuales

```python
def set_images(self, images)
```

**Propósito**: Establecer las imágenes para los diferentes tipos de power-ups.

**Parámetros**:

- `images`: Diccionario con imágenes para cada tipo de power-up

**Operaciones**:

- Asignar la imagen correspondiente al tipo
- Configurar el rectángulo y la hitbox
- Inicializar parámetros visuales específicos del tipo

## Tipos de Power-Ups

| Tipo       | Efecto                                | Duración    | Color    | Símbolo |
| ---------- | ------------------------------------- | ----------- | -------- | ------- |
| Shield     | Protege contra impactos               | 10 segundos | Azul     | Escudo  |
| Rapid Fire | Aumenta frecuencia y daño de disparos | 8 segundos  | Magenta  | Rayo    |
| Extra Life | Añade una vida                        | Permanente  | Verde    | Corazón |
| Speed      | Aumenta velocidad de movimiento       | 12 segundos | Amarillo | Bota    |

```python
# Selección de tipo aleatorio
if powerup_type == 'random':
    # Probabilidades: 40% escudo, 30% disparo rápido, 20% velocidad, 10% vida extra
    roll = random.random()
    if roll < 0.4:
        self.type = 'shield'
    elif roll < 0.7:
        self.type = 'rapid_fire'
    elif roll < 0.9:
        self.type = 'speed'
    else:
        self.type = 'extra_life'
else:
    self.type = powerup_type
```

## Ciclo de Vida

### Actualización

```python
def on_update(self)
```

**Propósito**: Actualizar la posición y estado del power-up en cada frame.

**Operaciones**:

1. Actualizar la posición vertical (caída)
2. Aplicar movimiento de oscilación lateral
3. Verificar tiempo de vida y activar parpadeo si está por expirar
4. Eliminar el power-up si ha expirado o salido de la pantalla

```python
# Movimiento descendente
self.y += self.speed
self.rect.y = int(self.y)

# Oscilación lateral
self.oscillation['angle'] += self.oscillation['speed']
offset_x = math.sin(math.radians(self.oscillation['angle'])) * self.oscillation['amplitude']
self.rect.x = int(self.x + offset_x)

# Verificar tiempo de vida
current_time = pygame.time.get_ticks()
time_alive = current_time - self.start_time

# Activar parpadeo si está próximo a expirar
if time_alive > self.lifetime * 0.7 and not self.is_flashing:
    self.is_flashing = True

# Parpadeo
if self.is_flashing:
    self.flash_timer += 1
    if self.flash_timer % 10 < 5:  # Alternar visibilidad
        self.visible = False
    else:
        self.visible = True

# Expiración por tiempo o salida de pantalla
if time_alive > self.lifetime or self.rect.top > SCREEN_HEIGHT + 50:
    self.should_destroy = True
```

### Efecto Visual

```python
def on_render(self, surface)
```

**Propósito**: Renderizar el power-up con efectos visuales específicos.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

1. Dibujar aura o efecto específico según el tipo
2. Dibujar el power-up con posible efecto de parpadeo
3. Añadir efectos de brillo o partículas

```python
# Solo dibujar si es visible (para parpadeo)
if self.visible:
    # Dibujar aura según tipo
    if self.type == 'shield':
        # Aura azul
        glow_surface = pygame.Surface((self.rect.width * 1.5, self.rect.height * 1.5), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (0, 150, 255, 100),
                           (glow_surface.get_width() // 2, glow_surface.get_height() // 2),
                           glow_surface.get_width() // 2)
        surface.blit(glow_surface,
                    (self.rect.centerx - glow_surface.get_width() // 2,
                     self.rect.centery - glow_surface.get_height() // 2))

    # Dibujar imagen del power-up
    super().on_render(surface)

    # Dibujar brillo según tipo (para rapid_fire, speed, etc.)
    # ...
```

## Sistema de Aplicación de Efectos

```python
def apply_effect(self, player)
```

**Propósito**: Aplicar el efecto del power-up al jugador.

**Parámetros**:

- `player`: Objeto jugador que recibe el efecto

**Operaciones**:

1. Identificar el tipo de power-up
2. Llamar al método correspondiente en el jugador
3. Reproducir sonido de power-up

```python
# Aplicar efecto según tipo
if self.type == 'shield':
    player.add_shield(3)  # Protección contra 3 impactos
elif self.type == 'rapid_fire':
    player.add_rapid_fire(0.3, 8000)  # 30% del cooldown normal, 8 segundos
elif self.type == 'extra_life':
    player.add_lives(1)  # Una vida extra
elif self.type == 'speed':
    player.add_speed_boost(1.5, 12000)  # 50% más rápido, 12 segundos
```

## Sistema de Colisiones

```python
def on_collide(self, other_entity)
```

**Propósito**: Manejar colisiones con otras entidades.

**Parámetros**:

- `other_entity`: Entidad con la que ha colisionado

**Comportamiento**:

- **Colisión con jugador**: Aplicar efecto y eliminarse
- **Colisión con otros objetos**: No interactúa

```python
# Verificar colisión con jugador
if hasattr(other_entity, 'entity_type') and other_entity.entity_type == 'player':
    # Aplicar efecto al jugador
    self.apply_effect(other_entity)

    # Emitir evento de power-up recogido
    self.emit_event("powerup_collected", {
        "type": self.type,
        "position": (self.rect.centerx, self.rect.centery)
    })

    # Reproducir sonido
    self.play_sound("powerup")

    # Eliminar power-up
    self.should_destroy = True
```

## Renderizado en Modo Debug

```python
def on_debug_draw(self, surface)
```

**Propósito**: Dibujar la hitbox y tipo en modo depuración.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

- Dibujar un rectángulo para visualizar la hitbox
- Mostrar tipo y tiempo de vida restante

```python
# Dibujar hitbox rectangular en modo debug
pygame.draw.rect(
    surface,
    (0, 255, 255),  # Color cyan
    self.rect,
    1  # Grosor de línea
)

# Mostrar tipo y tiempo restante
current_time = pygame.time.get_ticks()
time_alive = current_time - self.start_time
time_left = max(0, self.lifetime - time_alive)

font = pygame.font.SysFont(None, 16)
type_text = font.render(self.type, True, (255, 255, 255))
time_text = font.render(f"{time_left//1000}s", True, (255, 255, 255))

surface.blit(type_text, (self.rect.x, self.rect.y - 20))
surface.blit(time_text, (self.rect.x, self.rect.y - 10))
```

## Generación de Power-Ups

Los power-ups se generan principalmente cuando se destruyen meteoritos:

```python
# En SpaceShooterGame
def on_meteor_destroyed(self, data):
    """Maneja el evento de meteorito destruido"""
    position = data.get("position", (0, 0))
    size = data.get("size", "medium")
    score = data.get("score", 0)

    # Actualizar puntuación del jugador
    if self.player:
        self.player.add_score(score)

    # Posibilidad de generar power-up
    # Mayor probabilidad con meteoritos grandes
    spawn_chance = 0.05  # 5% base chance
    if size == "large":
        spawn_chance = 0.15  # 15% for large meteors
    elif size == "small":
        spawn_chance = 0.02  # 2% for small meteors

    if random.random() < spawn_chance:
        self.create_powerup(position[0], position[1])
```

```python
# En SpaceShooterGame
def create_powerup(self, x, y, powerup_type='random'):
    """Crea un nuevo power-up en la posición especificada"""
    powerup = PowerUp(x, y, powerup_type)

    # Configurar imágenes según tipo
    powerup_images = {
        'shield': self.resource_manager.get_image('powerup_shield'),
        'rapid_fire': self.resource_manager.get_image('powerup_rapid_fire'),
        'extra_life': self.resource_manager.get_image('powerup_life'),
        'speed': self.resource_manager.get_image('powerup_speed')
    }
    powerup.set_images(powerup_images)

    # Registrar en el motor
    self.register_object(powerup)
    return powerup
```

## Ejemplo de Uso

```python
# Ejemplo de generación programada de power-ups
def generate_scheduled_powerup(self):
    """Genera un power-up en posición aleatoria periódicamente"""
    if self.game_time > self.next_powerup_time:
        # Generar en posición aleatoria en la parte superior
        x = random.randint(50, self.width - 50)
        y = -20

        # Preferir power-ups de escudo en niveles difíciles
        if self.difficulty > 0.7:
            powerup_type = 'shield'
        else:
            powerup_type = 'random'

        # Crear power-up
        self.create_powerup(x, y, powerup_type)

        # Programar siguiente aparición (entre 30-60 segundos)
        self.next_powerup_time = self.game_time + random.randint(30000, 60000)
```

## Buenas Prácticas

1. **Feedback visual claro**: Cada tipo tiene colores y efectos distintivos
2. **Avisos de expiración**: Parpadeo cuando está próximo a desaparecer
3. **Equilibrio de juego**: Probabilidades ajustadas según dificultad y tipo
4. **Variedad de efectos**: Diferentes tipos de mejoras para estrategia
5. **Movimiento atractivo**: Oscilación para llamar la atención del jugador
6. **Recompensa por habilidad**: Mayor probabilidad en meteoritos difíciles
