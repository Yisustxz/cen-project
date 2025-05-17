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
- `hitbox_scale`: Factor de escala para la hitbox (1.0 = tamaño completo)
- `hitbox_padding`: Padding en píxeles (+ = expansión, - = reducción)

### Creación y Configuración

```python
def create_hitbox(self, scale=None, padding=None)
```

**Propósito**: Crear o actualizar la hitbox basada en la imagen actual.

**Parámetros**:

- `scale`: Factor de escala (1.0 = tamaño completo)
- `padding`: Padding en píxeles (- = reducción, + = expansión)

**Ejemplos**:

```python
# Hitbox más pequeña (para colisiones más precisas)
self.create_hitbox(padding=-10)  # 10 píxeles menos en cada lado

# Hitbox de un porcentaje del tamaño
self.create_hitbox(scale=0.8)  # 80% del tamaño del sprite

# Hitbox más grande (para áreas de detección)
self.create_hitbox(padding=5)  # 5 píxeles más en cada lado
```

### Activación/Desactivación

```python
def disable_hitbox(self)
```

**Propósito**: Desactivar la hitbox (objeto no colisionable).

```python
def enable_hitbox(self)
```

**Propósito**: Activar la hitbox (objeto colisionable).

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
        # El misil impacta y se destruye
        self.should_destroy = True
        # Notificar al juego para efectos visuales
        if self.game:
            self.game.emit_event("impact", {
                "x": self.x,
                "y": self.y,
                "projectile": self,
                "target": other_entity
            })
        return True
    return False
```

### Jugador recoge PowerUp

```python
# En la clase PowerUp
def on_collide(self, other_entity):
    if other_entity.type == "player":
        # Aplicar efecto al jugador
        if self.apply_effect(other_entity):
            # Notificar al juego
            if self.game:
                self.game.emit_event("powerup_collected", {
                    "type": self.powerup_type,
                    "x": self.x,
                    "y": self.y
                })
            # Eliminar el powerup
            self.kill()
            return True
    return False
```

### Jugador golpeado por Enemigo

```python
# En la clase Player
def on_collide(self, other_entity):
    if other_entity.type == "meteor" and self.invincibility_frames == 0:
        # Si tiene escudo, consumir un impacto
        if self.shield_remaining > 0:
            self.shield_remaining -= 1
            # Breve invencibilidad
            self.invincibility_frames = 20
            return True
        else:
            # Sin escudo, perder vida
            self.lives -= 1
            self.invincibility_frames = 50
            return True
    return False
```

## Buenas Prácticas

1. **Ajustar hitboxes adecuadamente**: Hitboxes más pequeñas que los sprites para mejor precisión
2. **Devolver True al manejar colisiones**: Esto ayuda a evitar manejadores duplicados
3. **No abusar de las colisiones**: Para detecciones de área considerar otros métodos
4. **Usar invencibilidad temporal**: Especialmente tras recibir daño, para evitar múltiples golpes
5. **Optimizar la detección**: Si hay muchos objetos, considerar técnicas como partición espacial
6. **Código de manejo claro**: Mantener los manejadores de colisión simples y directos
