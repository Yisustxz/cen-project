# Sistema de Sprites (GameObject)

La clase `GameObject` es la base para todas las entidades del juego. Proporciona la funcionalidad común que necesitan todos los objetos interactivos del juego, como posición, rotación, hitboxes, colisiones y visibilidad.

## Responsabilidades Principales

- **Gestión de posición y movimiento**
- **Sistema de hitboxes para colisiones**
- **Rotación de sprites**
- **Control de visibilidad**
- **Dibujado en pantalla**
- **Detección de colisiones**
- **Manejo de eventos del juego**

## Diagrama de Clase

```
+-------------------+
|    GameObject     |
+-------------------+
| - x, y            |
| - type            |
| - game            |
| - is_visible      |
| - angle           |
| - rotation_speed  |
| - image           |
| - original_image  |
| - rect            |
| - hitbox          |
| - has_hitbox      |
+-------------------+
| + update()        |
| + on_update()     |
| + draw()          |
| + draw_hitbox()   |
| + collides_with() |
| + on_game_event() |
| ...               |
+-------------------+
```

## Creación y Configuración

### Constructor

```python
def __init__(self, x, y, image=None, obj_type=None)
```

**Propósito**: Inicializar un objeto del juego con su posición y configuración básica.

**Parámetros**:

- `x`: Posición X inicial
- `y`: Posición Y inicial
- `image`: Imagen del objeto (opcional)
- `obj_type`: Tipo de objeto para clasificación (opcional)

**Operaciones**:

- Inicializa posición (x, y)
- Configura tipo de objeto (si no se especifica, usa el nombre de la clase)
- Inicializa imagen y rectángulo
- Inicializa hitbox básica

### Configuración de Imágenes

```python
def set_rotation(self, angle, speed=0)
```

**Propósito**: Configurar la rotación inicial y velocidad de rotación.

**Parámetros**:

- `angle`: Ángulo inicial en grados
- `speed`: Velocidad de rotación en grados por frame (opcional)

### Configuración de Hitbox

```python
def create_hitbox(self, scale=None, padding=None)
```

**Propósito**: Crear o actualizar la hitbox basada en la imagen actual.

**Parámetros**:

- `scale`: Factor de escala (1.0 = tamaño completo de la imagen)
- `padding`: Padding negativo (reducción) o positivo (expansión) en píxeles

**Ejemplo**:

```python
# Crear una hitbox más pequeña que la imagen (para colisiones más precisas)
self.create_hitbox(padding=-10)  # 10 píxeles menos en cada lado

# Crear una hitbox escalada (útil para objetos con formas complejas)
self.create_hitbox(scale=0.8)  # 80% del tamaño de la imagen
```

## Ciclo de Vida del Objeto

El ciclo de vida de un GameObject se gestiona principalmente a través de estos métodos:

### Actualización

```python
def update(self)
```

**Propósito**: Método principal de actualización llamado por el motor.

**Operaciones**:

1. Actualiza la posición del rectángulo basada en x, y
2. Actualiza la rotación si hay velocidad de rotación
3. Actualiza la posición de la hitbox
4. Llama a `on_update()` para la lógica específica de la clase derivada

```python
def on_update(self)
```

**Propósito**: Método que deben sobrescribir las clases derivadas para implementar su lógica específica.

**Ejemplo de Implementación**:

```python
def on_update(self):
    # Mover hacia abajo
    self.y += 2

    # Verificar si sale de la pantalla
    if self.y > 600:
        self.kill()
```

### Renderizado

```python
def draw(self, surface)
```

**Propósito**: Dibujar el objeto en la superficie proporcionada.

**Parámetros**:

- `surface`: Superficie de Pygame donde dibujar

**Operaciones**:

- Si el objeto es visible, dibuja la imagen en el rectángulo

```python
def draw_hitbox(self, surface, color=None)
```

**Propósito**: Dibujar la hitbox para depuración.

**Parámetros**:

- `surface`: Superficie de Pygame donde dibujar
- `color`: Color para dibujar la hitbox (opcional, se usa un color predeterminado según el tipo)

**Características**:

- Usa colores diferentes según el tipo de objeto
- Muestra el tamaño de la hitbox
- Solo se dibuja en modo debug

## Sistema de Colisiones

### Detección de Colisiones

```python
def collides_with(self, other)
```

**Propósito**: Comprobar si este objeto colisiona con otro.

**Parámetros**:

- `other`: Otro objeto GameObject

**Retorno**:

- `True` si hay colisión
- `False` en caso contrario

**Algoritmo**:

- Usa el método `colliderect` de Pygame para comprobar la intersección de hitboxes
- Solo comprueba si ambos objetos tienen hitbox habilitada

### Manejo de Colisiones

El manejo real de las colisiones debe implementarse en las clases derivadas a través del método:

```python
def on_collide(self, other_entity)
```

**Propósito**: Manejar la colisión con otra entidad.

**Parámetros**:

- `other_entity`: La entidad con la que ha colisionado

**Retorno**:

- `True` si la colisión fue manejada
- `False` en caso contrario

**Ejemplo de Implementación**:

```python
def on_collide(self, other_entity):
    if other_entity.type == "meteor":
        self.take_damage()
        return True
    return False
```

## Sistema de Eventos

Los objetos pueden recibir eventos del juego principal a través del método:

```python
def on_game_event(self, event_type, data=None)
```

**Propósito**: Manejar eventos emitidos por el juego.

**Parámetros**:

- `event_type`: Tipo de evento a manejar
- `data`: Datos asociados al evento (opcional)

**Retorno**:

- `True` si el evento fue manejado
- `False` en caso contrario

**Eventos Comunes**:

- `"game_over"`: Cuando el juego termina
- `"player_hit"`: Cuando el jugador es golpeado
- `"meteor_destroyed"`: Cuando un meteorito es destruido
- `"powerup_collected"`: Cuando se recoge un powerup

**Ejemplo de Implementación**:

```python
def on_game_event(self, event_type, data=None):
    if event_type == "game_over":
        self.speed = 0  # Detener movimiento
        return True
    return False
```

## Control de Visibilidad

```python
def set_visibility(self, visible)
```

**Propósito**: Establecer si el objeto es visible o no.

**Parámetros**:

- `visible`: `True` para hacer visible, `False` para invisible

```python
def toggle_visibility(self)
```

**Propósito**: Alternar el estado de visibilidad del objeto.

## Rotación de Imágenes

La rotación se maneja automáticamente en base a los valores de `angle` y `rotation_speed`:

```python
def update_rotation(self)
```

**Propósito**: Actualizar la rotación de la imagen y ajustar el rect y hitbox.

**Operaciones**:

1. Rota la imagen original al ángulo actual
2. Actualiza el rectángulo manteniendo el centro
3. Recalcula la hitbox para la imagen rotada

## Ejemplo de Uso

```python
class Enemy(GameObject):
    def __init__(self, x, y):
        # Cargar imagen
        image = pygame.image.load("enemy.png")
        super().__init__(x, y, image, "enemy")

        # Configurar hitbox más pequeña
        self.create_hitbox(padding=-5)

        # Configurar rotación
        self.set_rotation(0, 2)  # Rotar 2 grados por frame

        # Variables específicas
        self.health = 100
        self.speed = 1

    def on_update(self):
        # Mover hacia abajo
        self.y += self.speed

        # Verificar si sale de la pantalla
        if self.y > 600:
            if self.game:
                self.game.unregister_object(self)
            self.kill()

    def on_collide(self, other_entity):
        if other_entity.type == "missile":
            self.health -= 25
            if self.health <= 0:
                if self.game:
                    self.game.unregister_object(self)
                self.kill()
            return True
        return False

    def on_game_event(self, event_type, data=None):
        if event_type == "game_over":
            self.speed = 0
            return True
        return False
```

## Buenas Prácticas

1. **Usar `on_update()` para la lógica específica** en lugar de sobrescribir `update()`
2. **Manejar las colisiones en `on_collide()`** y devolver `True` si la colisión fue manejada
3. **Manejar los eventos del juego en `on_game_event()`** y devolver `True` si el evento fue manejado
4. **Ajustar las hitboxes** para una detección de colisiones más precisa
5. **Liberar recursos** desregistrando el objeto del motor cuando ya no se necesita
6. **Mantener la lógica simple** en cada objeto, delegando comportamientos complejos al motor
