# Missile

La clase `Missile` representa los proyectiles disparados por el jugador en Space Shooter. Estos objetos viajan hacia arriba en la pantalla y destruyen meteoritos al impactar contra ellos.

## Responsabilidades Principales

- **Movimiento ascendente** a velocidad constante
- **Colisión con meteoritos** causando daño
- **Destrucción automática** al salir de la pantalla o impactar
- **Efectos visuales** de propulsión y explosión al impactar
- **Manejo de diferentes tipos** de misiles (normal, mejorado)

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
|      Missile      |
+-------------------+
| - speed           |
| - damage          |
| - trail_particles |
| - owner           |
| - type            |
| ...               |
+-------------------+
| + on_update()     |
| + on_collide()    |
| + create_trail()  |
| ...               |
+-------------------+
```

## Atributos Principales

| Atributo           | Tipo       | Descripción                                |
| ------------------ | ---------- | ------------------------------------------ |
| `speed`            | float      | Velocidad de desplazamiento vertical       |
| `damage`           | int        | Cantidad de daño que causa al impactar     |
| `trail_particles`  | list       | Lista de partículas de estela              |
| `owner`            | GameObject | Referencia al objeto que disparó el misil  |
| `type`             | str        | Tipo de misil ('normal', 'enhanced', etc.) |
| `explosion_active` | bool       | Indica si la explosión está activa         |
| `explosion_frame`  | int        | Frame actual de la animación de explosión  |

## Inicialización

```python
def __init__(self, x, y, owner=None, missile_type='normal')
```

**Propósito**: Inicializar un misil con posición, propietario y tipo.

**Parámetros**:

- `x`: Posición X inicial
- `y`: Posición Y inicial
- `owner`: Referencia al objeto que disparó el misil (generalmente el jugador)
- `missile_type`: Tipo de misil ('normal', 'enhanced', etc.)

**Operaciones**:

- Llamar al constructor de la clase padre
- Inicializar velocidad, daño y otros atributos según el tipo
- Establecer la entidad propietaria
- Configurar la hitbox y efectos visuales iniciales

```python
def set_images(self, image, explosion_images=None)
```

**Propósito**: Establecer las imágenes para el misil y su explosión.

**Parámetros**:

- `image`: Imagen principal del misil
- `explosion_images`: Imágenes para la animación de explosión (opcional)

**Operaciones**:

- Asignar imágenes
- Configurar el rectángulo y la hitbox
- Inicializar recursos para la animación de explosión

## Tipos de Misiles

| Tipo     | Velocidad | Daño | Efectos Visuales  | Descripción                |
| -------- | --------- | ---- | ----------------- | -------------------------- |
| Normal   | 7.0       | 1    | Estela simple     | Misil estándar del jugador |
| Enhanced | 9.0       | 2    | Estela multicolor | Misil mejorado (power-up)  |

```python
# Configuración según tipo
if missile_type == 'enhanced':
    self.speed = 9.0
    self.damage = 2
    self.trail_color = (255, 100, 0)  # Naranja
else:  # normal
    self.speed = 7.0
    self.damage = 1
    self.trail_color = (0, 255, 255)  # Cyan
```

## Ciclo de Vida

### Actualización

```python
def on_update(self)
```

**Propósito**: Actualizar la posición y estado del misil en cada frame.

**Operaciones**:

1. Actualizar la posición vertical (movimiento ascendente)
2. Crear partículas de estela para efecto visual
3. Comprobar si ha salido de la pantalla
4. Actualizar la animación de explosión si está activa

```python
# Movimiento ascendente
self.y -= self.speed
self.rect.y = int(self.y)

# Crear estela de partículas
self.create_trail()

# Comprobar si ha salido de la pantalla
if self.rect.bottom < 0:
    self.should_destroy = True
```

### Efectos Visuales

```python
def create_trail(self)
```

**Propósito**: Crear partículas de estela detrás del misil.

**Operaciones**:

1. Crear nuevas partículas en la posición actual
2. Configurar propiedades visuales según el tipo de misil
3. Añadir las partículas a la lista de efectos

```python
# Crear partículas de estela
trail_particle = {
    'x': self.rect.centerx + random.randint(-2, 2),
    'y': self.rect.bottom + random.randint(0, 5),
    'size': random.randint(2, 4),
    'life': 10,
    'color': self.trail_color
}
self.trail_particles.append(trail_particle)
```

```python
def update_trail(self)
```

**Propósito**: Actualizar las partículas de la estela del misil.

**Operaciones**:

1. Actualizar posición y tamaño de cada partícula
2. Reducir la vida de las partículas
3. Eliminar partículas que hayan terminado su ciclo de vida

```python
# Actualizar partículas existentes
for particle in self.trail_particles[:]:
    particle['life'] -= 1
    if particle['life'] <= 0:
        self.trail_particles.remove(particle)
    else:
        particle['y'] += 1  # Las partículas caen lentamente
        particle['size'] *= 0.9  # Las partículas se encogen
```

### Sistema de Explosión

```python
def explode(self)
```

**Propósito**: Iniciar la animación de explosión del misil.

**Operaciones**:

1. Desactivar las colisiones
2. Activar la animación de explosión
3. Reproducir sonido de explosión

```python
# Activar animación de explosión
self.explosion_active = True
self.explosion_frame = 0
self.collidable = False  # Desactivar colisiones
```

## Sistema de Colisiones

```python
def on_collide(self, other_entity)
```

**Propósito**: Manejar colisiones con otras entidades.

**Parámetros**:

- `other_entity`: Entidad con la que ha colisionado

**Comportamiento**:

- **Colisión con meteorito**: Aplicar daño al meteorito e iniciar explosión
- **Colisión con jugador**: No hacer nada (ignorar colisión con el propietario)
- **Colisión con otros misiles**: No hacer nada

```python
# Comprobar colisión con meteorito
if hasattr(other_entity, 'entity_type') and other_entity.entity_type == 'meteor':
    # Aplicar daño al meteorito
    was_destroyed = other_entity.take_damage(self.damage)

    # Iniciar explosión del misil
    self.explode()

    # Asignar puntos al jugador si el meteorito fue destruido
    if was_destroyed and self.owner and hasattr(self.owner, 'add_score'):
        self.owner.add_score(other_entity.score_value)
```

## Renderizado

```python
def on_render(self, surface)
```

**Propósito**: Renderizar el misil y sus efectos visuales.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

1. Dibujar las partículas de la estela
2. Dibujar el misil o su explosión, según el estado

```python
# Dibujar partículas de estela
for particle in self.trail_particles:
    pygame.draw.circle(
        surface,
        particle['color'],
        (int(particle['x']), int(particle['y'])),
        int(particle['size'])
    )

# Dibujar el misil o su explosión
super().on_render(surface)
```

## Renderizado en Modo Debug

```python
def on_debug_draw(self, surface)
```

**Propósito**: Dibujar la hitbox en modo depuración.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

- Dibujar un rectángulo verde para visualizar la hitbox

```python
# Dibujar hitbox rectangular en modo debug
pygame.draw.rect(
    surface,
    (0, 255, 0),  # Color verde
    self.rect,
    1  # Grosor de línea
)
```

## Creación de Misiles

Los misiles se crean desde el jugador y se gestionan por `SpaceShooterGame`:

```python
# En el jugador (Player)
def fire_missile(self):
    """Dispara un misil si ha pasado el tiempo de recarga"""
    current_time = pygame.time.get_ticks()
    if current_time - self.last_missile > self.missile_cooldown:
        self.last_missile = current_time

        # Emitir evento para que el juego cree el misil
        self.emit_event("player_fire_missile", {
            "x": self.rect.centerx,
            "y": self.rect.top,
            "type": "enhanced" if self.rapid_fire > 0 else "normal"
        })

        # Reproducir sonido
        self.play_sound("laser")
```

```python
# En el juego (SpaceShooterGame)
def on_player_fire_missile(self, data):
    """Maneja el evento de disparo del jugador"""
    x = data.get("x", 0)
    y = data.get("y", 0)
    missile_type = data.get("type", "normal")

    # Crear misil
    missile = Missile(x, y, self.player, missile_type)
    missile.set_images(
        self.resource_manager.get_image('missile'),
        self.resource_manager.get_image_sequence('explosion_small', 5)
    )

    # Registrar misil en el motor
    self.register_object(missile)
```

## Ejemplo de Uso

```python
# En el método handle_input de Player
def handle_input(self, keys):
    # Movimiento
    if keys[pygame.K_LEFT]:
        self.x -= 5 * self.speed_boost
    if keys[pygame.K_RIGHT]:
        self.x += 5 * self.speed_boost

    # Disparo
    if keys[pygame.K_SPACE]:
        self.fire_missile()

    # Actualizar posición
    self.rect.x = int(self.x)
```

## Buenas Prácticas

1. **Separación de responsabilidades**: El misil solo se preocupa de su propio comportamiento
2. **Feedback visual**: Efectos de estela y explosión para mejor experiencia
3. **Extensibilidad**: Sistema flexible para diferentes tipos de misiles
4. **Comunicación por eventos**: El misil notifica sobre colisiones e impactos
5. **Optimización**: Limpieza automática al salir de la pantalla
6. **Manejo de propietario**: Evita colisiones con el objeto que lo disparó
