# ObjectsManager (Gestor de Objetos)

El `ObjectsManager` es un componente central del motor que se encarga de administrar todos los objetos del juego. Proporciona funcionalidades para registrar, actualizar, consultar y eliminar objetos, así como para detectar colisiones entre ellos.

## Responsabilidades Principales

- **Registrar y desregistrar objetos del juego**
- **Mantener colecciones de objetos organizadas por tipo**
- **Proporcionar métodos para consultar objetos específicos**
- **Detectar colisiones entre objetos**
- **Propagar eventos a los objetos registrados**

## Diagrama de Clase

```
+------------------+
|  ObjectsManager  |
+------------------+
| - game_objects   |
| - objects_by_type|
| - game           |
+------------------+
| + register()     |
| + unregister()   |
| + clear()        |
| + get_objects()  |
| + get_objects_by_type() |
| + count_objects_by_type() |
| + detect_collisions() |
| + emit_event()   |
| ...              |
+------------------+
```

## Inicialización

```python
def __init__(self, game=None)
```

**Propósito**: Inicializar el gestor de objetos.

**Parámetros**:

- `game`: Referencia al juego principal (opcional)

**Operaciones**:

- Inicializa colecciones vacías para almacenar objetos
- Guarda la referencia al juego principal

## Registro y Gestión de Objetos

### Registro de Objetos

```python
def register(self, game_object)
```

**Propósito**: Registrar un objeto para ser gestionado por el motor.

**Parámetros**:

- `game_object`: Objeto derivado de GameObject

**Operaciones**:

1. Asigna la referencia al juego principal al objeto
2. Añade el objeto a la lista principal de objetos
3. Clasifica el objeto por su tipo

**Ejemplo**:

```python
# Desde el motor:
player = Player(100, 100)
objects_manager.register(player)

# O más comúnmente, a través del GameEngine:
game.register_object(player)
```

### Eliminación de Objetos

```python
def unregister(self, game_object)
```

**Propósito**: Eliminar un objeto de la gestión del motor.

**Parámetros**:

- `game_object`: Objeto a eliminar

**Operaciones**:

1. Elimina el objeto de la lista principal
2. Elimina el objeto de la clasificación por tipo

```python
def clear(self)
```

**Propósito**: Eliminar todos los objetos registrados.

**Operaciones**:

- Vacía todas las colecciones de objetos

## Consulta de Objetos

### Obtener Todos los Objetos

```python
def get_objects(self)
```

**Propósito**: Obtener todos los objetos registrados.

**Retorno**:

- Lista de todos los objetos

### Filtrar por Tipo

```python
def get_objects_by_type(self, obj_type)
```

**Propósito**: Obtener objetos de un tipo específico.

**Parámetros**:

- `obj_type`: Tipo de objeto a filtrar

**Retorno**:

- Lista de objetos del tipo especificado

**Ejemplo**:

```python
# Obtener todos los meteoritos
meteors = objects_manager.get_objects_by_type("meteor")

# Aplicar una acción a todos los meteoritos
for meteor in meteors:
    meteor.speed_up()
```

### Contar Objetos por Tipo

```python
def count_objects_by_type(self, obj_type)
```

**Propósito**: Contar cuántos objetos de un tipo específico hay registrados.

**Parámetros**:

- `obj_type`: Tipo de objeto a contar

**Retorno**:

- Número de objetos del tipo especificado

### Filtrado Personalizado

```python
def filter_objects(self, filter_func)
```

**Propósito**: Filtrar objetos según una función personalizada.

**Parámetros**:

- `filter_func`: Función que recibe un objeto y devuelve True/False

**Retorno**:

- Lista de objetos que cumplen el criterio

**Ejemplo**:

```python
# Obtener meteoritos con baja salud
low_health_meteors = objects_manager.filter_objects(
    lambda obj: obj.type == "meteor" and obj.health < 50
)
```

### Objetos Cercanos

```python
def get_nearest_object(self, x, y, obj_type=None, max_distance=None)
```

**Propósito**: Encontrar el objeto más cercano a una posición.

**Parámetros**:

- `x`, `y`: Coordenadas de referencia
- `obj_type`: Tipo de objeto a buscar (opcional)
- `max_distance`: Distancia máxima a considerar (opcional)

**Retorno**:

- El objeto más cercano o None si no se encuentra ninguno

## Sistema de Colisiones

```python
def detect_collisions(self)
```

**Propósito**: Detectar y manejar colisiones entre objetos.

**Algoritmo**:

1. Para cada par de objetos:
   - Si ambos tienen hitbox habilitada:
     - Verifica si colisionan usando `collides_with()`
     - Si colisionan, llama a `on_collide()` en ambos objetos

**Optimizaciones**:

- Evita comprobar colisiones entre objetos del mismo tipo (opcional)
- No comprueba colisiones con objetos sin hitbox
- Solo notifica colisiones no manejadas previamente

## Sistema de Eventos

```python
def emit_event(self, event_type, data=None, target_type=None)
```

**Propósito**: Propagar un evento a los objetos registrados.

**Parámetros**:

- `event_type`: Tipo de evento a emitir
- `data`: Datos asociados al evento (opcional)
- `target_type`: Tipo de objeto al que dirigir el evento (opcional)

**Operaciones**:

1. Filtra los objetos según el tipo objetivo (si se especifica)
2. Para cada objeto filtrado:
   - Llama a `on_game_event(event_type, data)`
   - Cuenta cuántos objetos manejaron el evento

**Retorno**:

- Número de objetos que manejaron el evento

**Ejemplo**:

```python
# Notificar a todos los objetos que el juego ha terminado
handled_count = objects_manager.emit_event("game_over")

# Notificar solo a los meteoritos que aumente la velocidad
handled_count = objects_manager.emit_event(
    "speed_up",
    {"multiplier": 1.5},
    "meteor"
)
```

## Información de Depuración

```python
def print_debug_info(self)
```

**Propósito**: Imprimir información sobre los objetos registrados para depuración.

**Operaciones**:

- Imprime el número total de objetos
- Imprime el número de objetos por tipo
- Imprime información sobre hitboxes

## Ejemplo de Uso Interno

El `ObjectsManager` generalmente no se usa directamente por el desarrollador del juego, sino que es utilizado internamente por el `GameEngine`:

```python
# Dentro de GameEngine:

def register_object(self, game_object):
    return self.objects_manager.register(game_object)

def update(self):
    # Actualizar objetos
    self.objects_manager.update_all_objects()

    # Detectar colisiones
    self.objects_manager.detect_collisions()

    # Lógica específica del juego
    self.on_update()

def emit_event(self, event_type, data=None, target_type=None):
    return self.objects_manager.emit_event(event_type, data, target_type)
```

## Optimizaciones y Consideraciones

1. **Gestión eficiente de memoria**: Elimina referencias a objetos que ya no se usan
2. **Iteración segura**: Permite modificar colecciones durante la iteración
3. **Clasificación por tipo**: Mejora el rendimiento de las consultas por tipo
4. **Detección de colisiones optimizada**: Evita comprobaciones innecesarias
5. **Propagación selectiva de eventos**: Permite dirigir eventos a tipos específicos
