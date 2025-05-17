# Sistema de Colisiones

El sistema de colisiones en Space Shooter maneja la detección y respuesta a las interacciones físicas entre los diferentes objetos del juego, como la nave del jugador, meteoritos, misiles y power-ups.

## Visión General

El sistema de colisiones está diseñado con los siguientes objetivos:

- **Precisión**: Proporcionar detección de colisiones precisa con diferentes tipos de hitboxes
- **Eficiencia**: Optimizar el rendimiento evitando comprobaciones innecesarias
- **Flexibilidad**: Soportar diferentes formas de hitboxes (rectangulares y circulares)
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
                          | is_colliding()   |
                          | on_collide()     |
                          | on_debug_draw()  |
                          +------------------+
                               ^       ^
                              /         \
              +-------------+           +---------------+
              |  RectHitbox |           |  CircleHitbox |
              +-------------+           +---------------+
              | Player      |           | Meteor        |
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

## Tipos de Hitboxes

### Hitbox Rectangular

Utilizada principalmente por:

- Nave del jugador
- Misiles
- Power-ups
- Elementos de interfaz

**Implementación**:

```python
def is_colliding(self, other_entity):
    # Comprobación básica
    if not self.collidable or not other_entity.collidable:
        return False

    # Comprobación específica para hitboxes circulares
    if hasattr(other_entity, 'hitbox_radius'):
        return self._rect_circle_collision(other_entity)

    # Colisión entre rectángulos
    return self.rect.colliderect(other_entity.rect)
```

### Hitbox Circular

Utilizada principalmente por:

- Meteoritos (para colisiones más precisas con formas irregulares)

**Implementación**:

```python
def is_colliding(self, other_entity):
    # Comprobación básica
    if not self.collidable or not other_entity.collidable:
        return False

    # Distancia entre centros
    dx = self.rect.centerx - other_entity.rect.centerx
    dy = self.rect.centery - other_entity.rect.centery
    distance = math.sqrt(dx * dx + dy * dy)

    # Colisión con otro objeto circular
    if hasattr(other_entity, 'hitbox_radius'):
        return distance < (self.hitbox_radius + other_entity.hitbox_radius)

    # Colisión con rectángulo
    return self._circle_rect_collision(other_entity)
```

### Colisiones Mixtas

#### Círculo-Rectángulo

```python
def _circle_rect_collision(self, rect_entity):
    """Detección de colisión entre un círculo y un rectángulo"""
    # Encontrar el punto más cercano del rectángulo al centro del círculo
    closest_x = max(rect_entity.rect.left, min(self.rect.centerx, rect_entity.rect.right))
    closest_y = max(rect_entity.rect.top, min(self.rect.centery, rect_entity.rect.bottom))

    # Calcular distancia entre el centro del círculo y el punto más cercano
    dx = self.rect.centerx - closest_x
    dy = self.rect.centery - closest_y
    distance = math.sqrt(dx * dx + dy * dy)

    # Colisión si la distancia es menor que el radio
    return distance < self.hitbox_radius
```

## Implementación en el Motor

### En GameEngine

```python
def update(self):
    """Actualiza la lógica del juego y detecta colisiones"""
    # Actualizar todos los objetos
    self.objects_manager.update()

    # Detectar colisiones solo si no está en pausa
    if not self.paused:
        self.objects_manager.detect_collisions()
```

### En ObjectsManager

```python
def detect_collisions(self):
    """Detecta colisiones entre objetos registrados"""
    # Filtrar objetos colisionables y visibles
    collidable_objects = [obj for obj in self.objects if obj.collidable and obj.visible]

    # Comprobación de colisiones
    for i, obj1 in enumerate(collidable_objects):
        for obj2 in collidable_objects[i+1:]:
            # Evitar comprobaciones innecesarias entre objetos del mismo tipo
            if self._should_check_collision(obj1, obj2):
                # Comprobar colisión
                if obj1.is_colliding(obj2):
                    # Notificar a ambos objetos
                    obj1.on_collide(obj2)
                    obj2.on_collide(obj1)
```

```python
def _should_check_collision(self, obj1, obj2):
    """Determina si dos objetos deberían comprobar colisión"""
    # Ejemplo: Los misiles del jugador no colisionan entre sí
    if hasattr(obj1, 'entity_type') and hasattr(obj2, 'entity_type'):
        if obj1.entity_type == 'missile' and obj2.entity_type == 'missile':
            return False

    # Otros casos específicos...

    return True
```

## Respuesta a Colisiones

Cada tipo de entidad implementa su propio comportamiento en respuesta a colisiones:

### Jugador (Player)

```python
def on_collide(self, other_entity):
    """Maneja colisiones con otros objetos"""
    if hasattr(other_entity, 'entity_type'):
        # Colisión con meteorito
        if other_entity.entity_type == 'meteor':
            self.take_damage()
```

### Meteorito (Meteor)

```python
def on_collide(self, other_entity):
    """Maneja colisiones con otros objetos"""
    if hasattr(other_entity, 'entity_type'):
        # Colisión con misil
        if other_entity.entity_type == 'missile':
            # El misil maneja el daño
            pass
        # Colisión con jugador
        elif other_entity.entity_type == 'player':
            # El jugador maneja el daño
            pass
```

### Misil (Missile)

```python
def on_collide(self, other_entity):
    """Maneja colisiones con otros objetos"""
    if hasattr(other_entity, 'entity_type'):
        # Ignorar colisión con el propietario
        if other_entity == self.owner:
            return

        # Colisión con meteorito
        if other_entity.entity_type == 'meteor':
            # Aplicar daño al meteorito
            was_destroyed = other_entity.take_damage(self.damage)

            # Explotar misil
            self.explode()

            # Asignar puntos al jugador
            if was_destroyed and self.owner and hasattr(self.owner, 'add_score'):
                self.owner.add_score(other_entity.score_value)
```

### Power-Up

```python
def on_collide(self, other_entity):
    """Maneja colisiones con otros objetos"""
    if hasattr(other_entity, 'entity_type') and other_entity.entity_type == 'player':
        # Aplicar efecto al jugador
        self.apply_effect(other_entity)

        # Emitir evento
        self.emit_event("powerup_collected", {
            "type": self.type,
            "position": (self.rect.centerx, self.rect.centery)
        })

        # Eliminar power-up
        self.should_destroy = True
```

## Visualización de Hitboxes

En modo debug, las hitboxes se visualizan para facilitar la depuración:

```python
def on_debug_draw(self, surface):
    """Dibuja las hitboxes en modo debug"""
    if hasattr(self, 'hitbox_radius'):
        # Dibujar hitbox circular
        pygame.draw.circle(
            surface,
            (255, 0, 0),  # Color rojo
            (self.rect.centerx, self.rect.centery),
            self.hitbox_radius,
            1  # Grosor de línea
        )
    else:
        # Dibujar hitbox rectangular
        pygame.draw.rect(
            surface,
            (0, 255, 0),  # Color verde
            self.rect,
            1  # Grosor de línea
        )
```

## Activación del Modo Debug

```python
# En GameEngine
def toggle_debug(self):
    """Activa/desactiva el modo debug"""
    self.debug = not self.debug
```

## Optimizaciones

### Particionado Espacial

Para juegos con muchos objetos, se implementa un sistema de particionado espacial:

```python
def detect_collisions_optimized(self):
    """Detecta colisiones usando particionado espacial"""
    # Filtrar objetos colisionables y visibles
    collidable_objects = [obj for obj in self.objects if obj.collidable and obj.visible]

    # Crear particiones espaciales (cuadrícula)
    grid_size = 100  # Tamaño de celda en píxeles
    grid = {}

    # Asignar objetos a celdas
    for obj in collidable_objects:
        # Calcular celdas que ocupa el objeto
        cells = self._get_grid_cells(obj, grid_size)

        # Añadir objeto a cada celda
        for cell in cells:
            if cell not in grid:
                grid[cell] = []
            grid[cell].append(obj)

    # Comprobar colisiones solo entre objetos en las mismas celdas
    checked_pairs = set()
    for cell, cell_objects in grid.items():
        for i, obj1 in enumerate(cell_objects):
            for obj2 in cell_objects[i+1:]:
                # Evitar comprobar la misma pareja dos veces
                pair_id = tuple(sorted([id(obj1), id(obj2)]))
                if pair_id in checked_pairs:
                    continue

                checked_pairs.add(pair_id)

                # Comprobar colisión
                if self._should_check_collision(obj1, obj2) and obj1.is_colliding(obj2):
                    obj1.on_collide(obj2)
                    obj2.on_collide(obj1)
```

### Filtrado de Colisiones por Tipo

```python
# Matriz de colisiones (qué tipos colisionan con qué otros)
collision_matrix = {
    'player': ['meteor', 'powerup'],
    'missile': ['meteor'],
    'meteor': ['player', 'missile'],
    'powerup': ['player']
}

def _should_check_collision(self, obj1, obj2):
    """Comprueba si dos objetos deben colisionar según su tipo"""
    if hasattr(obj1, 'entity_type') and hasattr(obj2, 'entity_type'):
        type1, type2 = obj1.entity_type, obj2.entity_type
        return type2 in collision_matrix.get(type1, []) or type1 in collision_matrix.get(type2, [])
    return True
```

## Casos de Uso Comunes

### Jugador vs Meteorito

1. El meteorito cae desde la parte superior
2. La detección de colisiones detecta intersección entre hitboxes
3. Se llama a `on_collide` en ambos objetos
4. El jugador recibe daño o pierde una vida si no está protegido
5. El meteorito continúa su trayectoria

### Misil vs Meteorito

1. El misil viaja hacia arriba
2. Colisiona con un meteorito
3. El misil aplica daño al meteorito
4. El meteorito reduce su salud, posiblemente explotando
5. El misil se destruye (explota)
6. Si el meteorito es destruido, el jugador recibe puntos

### Jugador vs Power-Up

1. El power-up cae desde arriba
2. El jugador lo intercepta
3. El power-up aplica su efecto al jugador
4. El power-up se destruye
5. Se muestra un mensaje indicando el efecto

## Buenas Prácticas

1. **Hitboxes más pequeñas que los sprites**: Para mayor tolerancia y mejor jugabilidad
2. **Distinción visual clara**: Hitboxes circulares en rojo, rectangulares en verde
3. **Filtrado inteligente**: Evitar comprobaciones entre objetos que no interactúan
4. **Optimización espacial**: Uso de técnicas como particionado espacial para juegos con muchos objetos
5. **Feedback visual**: Proporcionar feedback al jugador durante colisiones (efectos de daño, explosiones)
6. **Invencibilidad temporal**: Implementar períodos de invencibilidad tras recibir daño
