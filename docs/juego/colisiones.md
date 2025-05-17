# Sistema de Colisiones

El sistema de colisiones en Space Shooter maneja la detección y respuesta a las interacciones físicas entre los diferentes objetos del juego, como la nave del jugador, meteoritos, misiles y power-ups.

## Visión General

El sistema de colisiones está diseñado con los siguientes objetivos:

- **Precisión**: Proporcionar detección de colisiones precisa utilizando hitboxes personalizadas
- **Eficiencia**: Optimizar el rendimiento evitando comprobaciones innecesarias
- **Consistencia**: Mantener hitboxes que no roten con los sprites para un comportamiento predecible
- **Extensibilidad**: Permitir añadir nuevos tipos de colisiones fácilmente
- **Visualización**: Ofrecer ayudas visuales en modo debug para depurar colisiones

## Arquitectura del Sistema

```
+------------------+      +------------------+
|   GameEngine     |      |  ObjectsManager  |
+------------------+      +------------------+
| update()         |----->| detect_collisions() |
+------------------+      +------------------+
                                  |
                                  v
                          +------------------+
                          |    GameObject    |
                          +------------------+
                          | set_hitbox_data()|
                          | collides_with()  |
                          | on_collide()     |
                          | update_hitbox()  |
                          +------------------+
                               ^       ^
                              /         \
              +-------------+           +---------------+
              |  Player     |           | Meteor        |
              +-------------+           +---------------+
              | Missile     |           |               |
              | PowerUp     |           |               |
              +-------------+           +---------------+
```

## Proceso de Detección de Colisiones

1. **Filtrado Inicial**: Se filtran los objetos no colisionables o invisibles
2. **Optimización Espacial**: Se agrupan objetos por regiones para reducir comprobaciones
3. **Detección de Colisión**: Se comprueba intersección entre hitboxes
4. **Notificación**: Se informa a ambos objetos involucrados
5. **Respuesta**: Cada objeto implementa su respuesta específica a la colisión

## Sistema de Hitboxes

Todas las entidades del juego utilizan un sistema unificado de hitboxes rectangulares que no rotan con el sprite.

### Configuración de la Hitbox

Cada entidad define sus datos de hitbox mediante un diccionario con las siguientes propiedades:

```python
hitbox_data = {
    "width": 20,     # Ancho de la hitbox en píxeles
    "height": 40,    # Alto de la hitbox en píxeles
    "offset_x": 0,   # Desplazamiento horizontal (opcional, 0 por defecto)
    "offset_y": 0    # Desplazamiento vertical (opcional, 0 por defecto)
}
```

### Aplicación de la Hitbox

Para aplicar la hitbox a una entidad, se usa el método `set_hitbox_data()`:

```python
def __init__(self, x, y):
    super().__init__(x, y, None, "player")

    # Cargar datos de configuración
    self.hitbox_data = PlayerData.get_player_hitbox_data()

    # Aplicar hitbox
    self.set_hitbox_data(self.hitbox_data)
```

### Actualización Automática

La posición de la hitbox se actualiza automáticamente cuando:

- La entidad se mueve
- La entidad cambia de posición
- Se llama a `update()` en cada frame

El sistema garantiza que la hitbox mantiene su forma, incluso cuando la imagen del sprite rota.

## Implementación por Entidades

### Jugador (Player)

```python
def __init__(self, x, y):
    super().__init__(x, y, None, "player")

    # Cargar datos de configuración
    self.hitbox_data = PlayerData.get_player_hitbox_data()

    # Aplicar hitbox
    self.set_hitbox_data(self.hitbox_data)

def on_collide(self, other_entity):
    """Maneja colisiones con otros objetos"""
    if other_entity.type == "meteor" and self.invincibility_frames == 0:
        self.take_damage()
        return True
    return False
```

### Meteorito (Meteor)

```python
def __init__(self, image, meteor_type, data, position, speed, rotation):
    # Posición proporcionada por el meteor_manager
    x, y = position

    # Guardar los datos para la hitbox
    self.hitbox_data = data

    # Inicializar GameObject
    super().__init__(x, y, image, obj_type="meteor")

    # Aplicar hitbox usando los datos de configuración
    self.set_hitbox_data(self.hitbox_data)

def on_collide(self, other_entity):
    """Maneja colisiones con otros objetos"""
    if other_entity.type == "missile":
        # Obtener el daño desde el misil
        missile_damage = other_entity.get_damage() if hasattr(other_entity, 'get_damage') else 1
        return self.take_damage(missile_damage)
    return False
```

### Misil (Missile)

```python
def __init__(self, x, y):
    # Inicializar primero sin imagen
    super().__init__(x, y, None, obj_type="missile")

    # Cargar datos de configuración
    self.hitbox_data = PlayerData.get_missile_hitbox_data()

    # Reducir el tamaño del hitbox para mayor precisión
    self.hitbox_data["width"] = int(self.hitbox_data["width"] * 0.7)
    self.hitbox_data["height"] = int(self.hitbox_data["height"] * 0.7)

    # Aplicar hitbox con los datos ajustados
    self.set_hitbox_data(self.hitbox_data)

def on_collide(self, other_entity):
    """Maneja colisiones con otros objetos"""
    if other_entity.type == "meteor" and not self.has_hit:
        self.has_hit = True
        self.should_destroy = True
        return True
    return False
```

## Visualización de Hitboxes

En modo debug (F3), el juego muestra las hitboxes de todos los objetos:

```python
def draw_debug(self, surface):
    """Dibuja información de depuración sobre el objeto"""
    # Si no hay modo debug, no hacer nada
    if not self.game or not self.game.debug_mode:
        return

    # Dibujar hitbox
    self.draw_hitbox(surface)

    # Mostrar centro del objeto
    pygame.draw.circle(
        surface,
        self.DEBUG_SPRITE_CENTER_COLOR,
        (int(self.x), int(self.y)),
        self.DEBUG_CENTER_SIZE
    )
```

## Consideraciones Especiales

### Offset para Ajuste Fino

Los valores `offset_x` y `offset_y` permiten ajustar con precisión la posición de la hitbox relativa al sprite:

```python
# Ejemplo de configuración en entities_config.json
"missile": {
    "speed": 500,
    "damage": 1,
    "hitbox_width": 8,
    "hitbox_height": 16,
    "offset_x": -4,   # Ajusta 4 píxeles a la izquierda
    "offset_y": -8    # Ajusta 8 píxeles hacia arriba
}
```

### Hitboxes Estáticas (No Rotantes)

Una característica importante del sistema es que las hitboxes **NO rotan** cuando el sprite rota:

```python
def update_rotation(self):
    """
    Actualiza la rotación de la imagen, pero NO DEL HITBOX.
    El hitbox se mantiene con su forma y dimensiones originales.
    """
    if self.original_image is not None:
        # Rotar la imagen
        self.image = pygame.transform.rotate(self.original_image, self.angle)
```

Esto proporciona un comportamiento consistente y predecible para las colisiones, independientemente de la rotación visual del objeto.

## Ejemplos Prácticos

### Configuración de Hitbox para el Jugador

```python
# En la clase Player
def __init__(self, x, y):
    super().__init__(x, y, None, "player")

    # Cargar datos de configuración
    self.hitbox_data = PlayerData.get_player_hitbox_data()

    # Aplicar hitbox
    self.set_hitbox_data(self.hitbox_data)
```

### Configuración de Hitbox para Meteoritos

```python
# En meteor_manager.py
def create_meteor(self, meteor_type, position=None):
    # Obtener datos de configuración
    meteor_data = MeteorData.get_meteor_config(meteor_type)

    # La configuración ya incluye los datos de hitbox:
    # - hitbox_width
    # - hitbox_height
    # - offset_x
    # - offset_y

    # Crear el meteorito
    meteor = Meteor(
        self.resource_manager.get_meteor_image(meteor_type),
        meteor_type,
        meteor_data,  # Pasar los datos completos, incluyendo hitbox
        position or self._generate_random_position(),
        self._generate_random_speed(meteor_data),
        self._generate_random_rotation(meteor_data)
    )
```

### Configuración de Hitbox para Misiles

```python
# En la clase Missile
def __init__(self, x, y):
    super().__init__(x, y, None, obj_type="missile")

    # Cargar datos de configuración
    self.hitbox_data = PlayerData.get_missile_hitbox_data()

    # Reducir el tamaño del hitbox para mayor precisión
    self.hitbox_data["width"] = int(self.hitbox_data["width"] * 0.7)
    self.hitbox_data["height"] = int(self.hitbox_data["height"] * 0.7)

    # Ajustar offsets para centrar correctamente el hitbox
    self.hitbox_data["offset_x"] = -4
    self.hitbox_data["offset_y"] = -8

    # Aplicar hitbox con los datos ajustados
    self.set_hitbox_data(self.hitbox_data)
```

## Buenas Prácticas

1. **Ser específico con las dimensiones**: Siempre definir dimensiones exactas de hitbox, no basarse en dimensiones de la imagen
2. **Usar offsets para ajuste fino**: Utilizar offset_x y offset_y para posicionar con precisión la hitbox
3. **Verificar colisiones visualmente**: Usar el modo debug (F3) para comprobar que las hitboxes se ajustan correctamente
4. **Modularizar la configuración**: Mantener los datos de hitbox en archivos de configuración
5. **Consistencia en la implementación**: Todas las entidades deben usar set_hitbox_data() para tener colliders válidos
