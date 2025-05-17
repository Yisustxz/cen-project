# Sistema de Colisiones

El sistema de colisiones es una parte fundamental del motor de juego, que permite detectar y manejar las interacciones físicas entre objetos. Este sistema se basa en hitboxes rectangulares y un algoritmo de detección optimizado.

## Arquitectura del Sistema

El sistema de colisiones se distribuye entre tres componentes principales:

1. **GameObject**: Define las hitboxes y el método `collides_with()` para comprobar colisiones
2. **ObjectsManager**: Implementa el algoritmo de detección mediante `detect_collisions()`
3. **Clases derivadas**: Implementan `on_collide()` para definir el comportamiento al colisionar

## Hitboxes

### Concepto y Propósito

Las hitboxes son áreas rectangulares utilizadas para detectar colisiones, generalmente más pequeñas que los sprites visuales para mejorar la precisión.

```
┌───────────────────┐
│                   │
│     Sprite        │
│                   │
│     ┌─────┐       │
│     │     │       │
│     │Hitbox│      │
│     │     │       │
│     └─────┘       │
│                   │
└───────────────────┘
```

### Implementación en GameObject

Cada GameObject tiene una hitbox definida por:

- `hitbox`: Un rectángulo de Pygame (pygame.Rect)
- `has_hitbox`: Un booleano que indica si la hitbox está activa
- `hitbox_data`: Un diccionario con los datos de configuración de la hitbox

### Creación y Configuración

```python
def set_hitbox_data(self, data)
```

**Propósito**: Establecer los datos de la hitbox personalizada. Este método DEBE ser llamado para tener un hitbox válido.

**Parámetros**:

- `data`: Diccionario con datos de configuración de la hitbox
  - Debe contener: `width`/`height` (dimensiones exactas de la hitbox)
  - Opcional: `offset_x`/`offset_y` (desplazamiento desde el centro)

**Ejemplos**:

```python
# Hitbox personalizada con dimensiones específicas
self.set_hitbox_data({
    "width": 20,
    "height": 40
})

# Hitbox con desplazamiento respecto al centro
self.set_hitbox_data({
    "width": 20,
    "height": 40,
    "offset_x": 5,
    "offset_y": -3
})
```

### Actualización de la Hitbox

```python
def update_hitbox(self)
```

**Propósito**: Actualiza la posición de la hitbox basada en la posición del objeto y los datos de hitbox configurados.

**Notas**:

- La hitbox no rota cuando el sprite rota
- Esta función se llama automáticamente cuando cambia la posición del objeto

### Activación/Desactivación

```python
def disable_hitbox(self)
```

**Propósito**: Desactivar la hitbox (objeto no colisionable).

```python
def enable_hitbox(self)
```

**Propósito**: Activar la hitbox si hay datos de hitbox disponibles (objeto colisionable).

## Detección de Colisiones

### Comprobación Individual

A nivel de GameObject, el método `collides_with()` comprueba si este objeto colisiona con otro:

```python
def collides_with(self, other)
```

**Propósito**: Comprobar si dos objetos colisionan.

**Parámetros**:

- `other`: Otro objeto GameObject

**Retorno**:

- `True` si hay colisión
- `False` en caso contrario

**Implementación**:

```python
def collides_with(self, other):
    if not (self.has_hitbox and hasattr(other, 'has_hitbox') and other.has_hitbox):
        return False
    return self.hitbox.colliderect(other.hitbox)
```

### Detección Global

A nivel de ObjectsManager, el método `detect_collisions()` comprueba todas las posibles colisiones:

```python
def detect_collisions(self)
```

**Propósito**: Detectar y manejar todas las colisiones entre objetos.

**Algoritmo**:

1. Obtener todos los objetos registrados
2. Para cada par de objetos `(obj1, obj2)`:
   - Si ambos tienen hitbox activa:
     - Comprobar colisión con `obj1.collides_with(obj2)`
     - Si hay colisión, notificar a ambos objetos
   - Optimización: Evitar comprobar colisiones entre objetos del mismo tipo (opcional)

**Implementación Simplificada**:

```python
def detect_collisions(self):
    objects = self.get_objects()
    handled_collisions = set()

    for i, obj1 in enumerate(objects):
        for obj2 in objects[i+1:]:  # Solo comprobar pares únicos
            # Optimización: evitar colisiones entre objetos del mismo tipo
            if obj1.type == obj2.type:
                continue

            # Comprobar colisión
            if obj1.collides_with(obj2):
                # Crear un identificador único para esta colisión
                collision_id = (id(obj1), id(obj2))

                # Evitar notificar la misma colisión varias veces en el mismo frame
                if collision_id not in handled_collisions:
                    # Notificar a cada objeto
                    handled1 = obj1.on_collide(obj2)
                    handled2 = obj2.on_collide(obj1)

                    # Recordar que ya se ha manejado esta colisión
                    if handled1 or handled2:
                        handled_collisions.add(collision_id)
```

## Manejo de Colisiones

El manejo real de las colisiones se implementa en las clases derivadas a través del método `on_collide()`:

```python
def on_collide(self, other_entity)
```

**Propósito**: Definir el comportamiento cuando este objeto colisiona con otro.

**Parámetros**:

- `other_entity`: El objeto con el que ha colisionado

**Retorno**:

- `True` si la colisión fue manejada
- `False` en caso contrario

**Ejemplos de Implementación**:

```python
# En la clase Player
def on_collide(self, other_entity):
    if other_entity.type == "meteor" and self.invincibility_frames == 0:
        # Perder vida al chocar con un meteorito
        self.take_damage()
        return True
    elif other_entity.type == "powerup":
        # No hacemos nada, el powerup maneja la colisión
        return False
    return False

# En la clase Meteor
def on_collide(self, other_entity):
    if other_entity.type == "missile":
        # Recibir daño al ser alcanzado por un misil
        self.take_damage()
        return True
    return False

# En la clase Missile
def on_collide(self, other_entity):
    if other_entity.type == "meteor" and not self.has_hit:
        # Marcar el misil para ser destruido
        self.has_hit = True
        self.should_destroy = True
        return True
    return False
```

## Visualización de Hitboxes

Para depuración, es posible visualizar las hitboxes de todos los objetos:

```python
def draw_hitbox(self, surface, color=None)
```

**Propósito**: Dibujar la hitbox en la superficie para depuración.

**Parámetros**:

- `surface`: Superficie donde dibujar
- `color`: Color para la hitbox (opcional)

**Características**:

- Colores diferentes según el tipo de objeto
- Etiqueta con el tamaño de la hitbox
- Solo se dibuja cuando el modo debug está activado

**Activación**:
El modo debug se activa pulsando F3 durante el juego, lo que muestra todas las hitboxes.

## Optimizaciones

El sistema incluye varias optimizaciones para mejorar el rendimiento:

1. **Filtrado por tipo**: Evita comprobar colisiones entre objetos del mismo tipo (como entre dos meteoritos)
2. **Detección única por frame**: Evita notificar la misma colisión varias veces en el mismo frame
3. **Hitboxes ajustadas**: Usar hitboxes más pequeñas que los sprites reduce falsos positivos
4. **Desactivación selectiva**: Objetos pueden desactivar su hitbox temporalmente
5. **Comprobación de precondiciones**: Evita cálculos innecesarios verificando que ambos objetos tengan hitbox

## Casos de Uso Comunes

### Proyectil impacta Enemigo

```python
# En la clase Missile
def on_collide(self, other_entity):
    if other_entity.type == "meteor":
        # Notificar al juego que el misil impactó
        self.game.emit_event("missile_hit", {
            "missile": self,
            "meteor": other_entity
        })
        return True
```

### Jugador recoge Power-up

```python
# En la clase PowerUp
def on_collide(self, other_entity):
    if other_entity.type == "player":
        # Aplicar poder al jugador
        other_entity.apply_powerup(self.powerup_type)

        # Notificar al juego
        self.game.emit_event("powerup_collected", {
            "powerup_type": self.powerup_type,
            "player": other_entity
        })

        # Destruir el powerup
        self.destroy()
        return True
    return False
```

### Jugador impacta Enemigo

```python
# En la clase Player
def on_collide(self, other_entity):
    if other_entity.type == "meteor" and self.invincibility_frames == 0:
        # Recibir daño
        self.take_damage()

        # Notificar al juego
        self.game.emit_event("player_hit", {
            "player": self,
            "meteor": other_entity
        })
        return True
    return False
```

## Consideraciones Importantes

1. **Rendimiento**: Evitar realizar operaciones costosas en métodos `on_collide()`, ya que pueden ejecutarse muchas veces por frame

2. **Manejo Bidireccional**: Recordar que ambos objetos en una colisión reciben la notificación, por lo que el manejo debe coordinarse para evitar efectos duplicados

3. **Prioridad de Respuesta**: Por convención, el objeto con más "autoridad" sobre la colisión debería manejarla, por ejemplo:

   - Power-ups manejan colisión con jugador
   - Misiles manejan colisión con meteoritos
   - Jugador maneja colisión con enemigos

4. **Hitboxes Estáticas**: Las hitboxes no rotan con el sprite, lo que mantiene el comportamiento consistente aunque la imagen rote
