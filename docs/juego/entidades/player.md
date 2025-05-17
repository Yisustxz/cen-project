# Player

La clase `Player` representa la nave del jugador en el juego Space Shooter. Esta entidad es controlada por el usuario, puede disparar misiles, colisionar con meteoritos y recoger power-ups.

## Responsabilidades Principales

- **Movimiento lateral** controlado por el usuario
- **Disparo de misiles**
- **Gestión de vidas y daño**
- **Recepción de power-ups**
- **Manejo de colisiones con meteoritos**
- **Visualización de efectos de daño y power-ups**

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
|      Player       |
+-------------------+
| - lives           |
| - score           |
| - damage_image    |
| - invincibility_frames |
| - missile_cooldown |
| - last_missile    |
| - shield_remaining |
| - speed_boost     |
| - rapid_fire      |
| ...               |
+-------------------+
| + handle_input()  |
| + take_damage()   |
| + add_score()     |
| + add_shield()    |
| + draw_damage()   |
| ...               |
+-------------------+
```

## Atributos Principales

| Atributo               | Tipo    | Descripción                                            |
| ---------------------- | ------- | ------------------------------------------------------ |
| `lives`                | int     | Número de vidas restantes del jugador                  |
| `score`                | int     | Puntuación acumulada                                   |
| `damage_image`         | Surface | Imagen que se muestra cuando recibe daño               |
| `invincibility_frames` | int     | Contador de frames de invencibilidad tras recibir daño |
| `missile_cooldown`     | int     | Tiempo de recarga entre disparos en milisegundos       |
| `last_missile`         | int     | Timestamp del último disparo                           |
| `shield_remaining`     | int     | Impactos que puede absorber el escudo                  |
| `speed_boost`          | float   | Multiplicador de velocidad (power-up)                  |
| `rapid_fire`           | float   | Multiplicador de frecuencia de disparo (power-up)      |

## Inicialización

```python
def __init__(self, x, y)
```

**Propósito**: Inicializar el jugador con su posición inicial.

**Parámetros**:

- `x`: Posición X inicial
- `y`: Posición Y inicial

**Operaciones**:

- Llamar al constructor de la clase padre
- Inicializar vidas, puntuación y contadores
- Configurar valores iniciales para power-ups

```python
def set_images(self, image, damage_image)
```

**Propósito**: Establecer las imágenes para el jugador.

**Parámetros**:

- `image`: Imagen principal del jugador
- `damage_image`: Imagen que se muestra al recibir daño

**Operaciones**:

- Asignar imágenes
- Configurar el rectángulo y la hitbox
- Ajustar la posición de la hitbox (más pequeña que el sprite)

## Ciclo de Vida

### Actualización

```python
def on_update(self)
```

**Propósito**: Actualizar el estado del jugador en cada frame.

**Operaciones**:

1. Ajustar la posición de la hitbox
2. Gestionar el efecto de parpadeo durante invencibilidad
3. Actualizar estados de power-ups (duración, efectos)

### Renderizado

```python
def draw_damage(self, surface)
```

**Propósito**: Dibujar el efecto de daño y los efectos visuales de power-ups.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

1. Dibujar efectos visuales de power-ups activos
2. Dibujar efecto de daño si está activo

```python
def draw_powerup_effects(self, surface)
```

**Propósito**: Dibujar efectos visuales para power-ups activos.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

- Dibujar un escudo si está activo
- Dibujar indicadores de disparo rápido
- Dibujar efecto de estela para velocidad aumentada

## Manejo de Entradas

```python
def handle_input(self, keys)
```

**Propósito**: Procesar entradas del teclado para movimiento y disparo.

**Parámetros**:

- `keys`: Estado actual de las teclas

**Operaciones**:

1. Mover izquierda/derecha según teclas
2. Disparar misil si se pulsa la barra espaciadora
3. Aplicar modificadores de power-ups al movimiento y disparo

**Controles**:

- `LEFT`: Mover a la izquierda
- `RIGHT`: Mover a la derecha
- `SPACE`: Disparar misil

## Sistema de Daño

```python
def take_damage(self)
```

**Propósito**: Aplicar daño al jugador si no está en estado de invencibilidad.

**Retorno**:

- `True` si se aplicó daño
- `False` si el jugador estaba en invencibilidad o protegido por escudo

**Operaciones**:

1. Verificar si el jugador está en estado de invencibilidad
2. Si tiene escudo, consumir un impacto del escudo
3. Si no tiene escudo, reducir vidas y activar invencibilidad
4. Activar efecto visual de parpadeo

## Sistema de Colisiones

```python
def on_collide(self, other_entity)
```

**Propósito**: Manejar colisiones con otras entidades.

**Parámetros**:

- `other_entity`: Entidad con la que ha colisionado

**Comportamiento**:

- **Colisión con meteorito**: Recibir daño si no está en invencibilidad
- **Colisión con power-up**: No hace nada (el power-up maneja la colisión)

## Sistema de Eventos

```python
def on_game_event(self, event_type, data=None)
```

**Propósito**: Manejar eventos emitidos por el juego.

**Parámetros**:

- `event_type`: Tipo de evento a manejar
- `data`: Datos asociados al evento (opcional)

**Eventos Manejados**:

- **"game_over"**: Asegurar visibilidad en game over
- **"meteor_destroyed"**: Reaccionar si el meteorito explotó cerca

## Sistema de Power-ups

### Gestión de Power-ups

```python
def _update_powerups(self)
```

**Propósito**: Actualizar el estado de los power-ups activos.

**Operaciones**:

- Decrementar contadores de duración
- Desactivar efectos cuando expiran

### Aplicación de Power-ups

```python
def add_shield(self, value)
```

**Propósito**: Añadir un escudo al jugador.

```python
def add_speed_boost(self, multiplier, duration)
```

**Propósito**: Añadir un impulso de velocidad.

```python
def add_rapid_fire(self, cooldown_multiplier, duration)
```

**Propósito**: Añadir disparo rápido.

```python
def add_lives(self, lives)
```

**Propósito**: Añadir vidas adicionales.

## Sistema de Puntuación

```python
def add_score(self, points)
```

**Propósito**: Añadir puntos al marcador del jugador.

**Parámetros**:

- `points`: Cantidad de puntos a añadir

## Visualización de Efectos

### Escudo

El escudo se visualiza como un círculo semitransparente alrededor del jugador:

```python
# Crear un círculo semitransparente alrededor del jugador
shield_radius = max(self.rect.width, self.rect.height) + 10
shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
pygame.draw.circle(shield_surface, (0, 200, 255, 80), (shield_radius, shield_radius), shield_radius)
pygame.draw.circle(shield_surface, (0, 200, 255, 150), (shield_radius, shield_radius), shield_radius, 2)
```

### Disparo Rápido

El disparo rápido se visualiza como pequeños puntos alrededor del jugador:

```python
# Dibujar pequeños puntos alrededor del jugador
for i in range(8):
    angle = i * 45
    radius = self.rect.width + 5
    x = self.rect.centerx + radius * math.cos(math.radians(angle))
    y = self.rect.centery + radius * math.sin(math.radians(angle))
    pygame.draw.circle(surface, (255, 0, 255), (int(x), int(y)), 3)
```

### Impulso de Velocidad

El impulso de velocidad se visualiza como una estela detrás del jugador:

```python
# Dibujar estela detrás del jugador
trail_surface = pygame.Surface((self.rect.width, self.rect.height * 1.5), pygame.SRCALPHA)
for i in range(3):
    alpha = 150 - (i * 50)  # Más transparente cuanto más lejos
    trail_color = (255, 255, 0, alpha)
    trail_height = self.rect.height // 3
    trail_rect = pygame.Rect(0, i * trail_height, self.rect.width, trail_height)
    pygame.draw.rect(trail_surface, trail_color, trail_rect)
```

## Ejemplo de Uso

```python
# En el método init_game de SpaceShooterGame
def init_game(self):
    # Cargar imágenes
    spaceship_img = self.resource_manager.get_image('spaceship')
    damage_img = self.resource_manager.get_image('damage')

    # Inicializar el jugador
    player = Player(PLAYER_START_X, PLAYER_START_Y)
    player.set_images(spaceship_img, damage_img)

    # Registrar el jugador en el motor
    self.register_object(player)
```

## Buenas Prácticas

1. **Invencibilidad temporal**: Después de recibir daño, el jugador es invencible brevemente
2. **Efectos visuales claros**: Los power-ups tienen efectos visuales distintivos
3. **Colisiones precisas**: La hitbox es más pequeña que el sprite para mejorar la jugabilidad
4. **Mínimo acoplamiento**: El jugador solo depende del motor y no de otras entidades
5. **Comportamiento autónomo**: Maneja su propio movimiento, disparo y efectos
6. **Comunicación por eventos**: Notifica al juego de acciones importantes mediante eventos
