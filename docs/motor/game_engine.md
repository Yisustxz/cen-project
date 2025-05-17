# GameEngine (Motor de Juego)

La clase `GameEngine` es el núcleo central del motor de juego. Se encarga de coordinar todos los aspectos del juego: inicialización, bucle principal, manejo de eventos, actualización y renderizado.

## Responsabilidades Principales

- **Gestión del bucle principal de juego**
- **Manejo de eventos de Pygame**
- **Control de FPS**
- **Inicialización y limpieza de recursos**
- **Coordinación de la actualización y renderizado**
- **Gestión de colisiones entre objetos**
- **Sistema de eventos personalizado**

## Diagrama de Clase

```
+-------------------+
|    GameEngine     |
+-------------------+
| - objects_manager |
| - running         |
| - paused          |
| - clock           |
| - debug_mode      |
| - game_window     |
+-------------------+
| + __init__()      |
| + run()           |
| + update()        |
| + render()        |
| + handle_events() |
| + quit()          |
| + register_object()|
| + emit_event()    |
| ...               |
+-------------------+
```

## Ciclo de Vida

El ciclo de vida del motor sigue un patrón secuencial claro:

1. **Inicialización** - Ejecutada al crear una instancia del motor
2. **Bucle Principal** - Ejecutado repetidamente hasta que el juego termina
3. **Limpieza** - Ejecutada al finalizar el juego

### Métodos del Ciclo de Vida

```
┌─────────────────┐
│   __init__()    │ Inicialización base del motor
└───────┬─────────┘
        ▼
┌─────────────────┐
│   init_game()   │ Inicialización específica (debe ser implementada por la clase derivada)
└───────┬─────────┘
        ▼
┌─────────────────┐
│     run()       │ Ejecución del bucle principal
└───────┬─────────┘
        ▼
┌─────────────────┐
│   cleanup()     │ Limpieza de recursos
└─────────────────┘
```

## Bucle Principal (Game Loop)

El bucle principal es gestionado por el método `run()`, que se encarga de ejecutar repetidamente las siguientes fases:

```
┌─────────────────┐
│ handle_events() │ Manejo de eventos de Pygame
└───────┬─────────┘
        ▼
┌─────────────────┐
│    update()     │ Actualización de la lógica
└───────┬─────────┘
        ▼
┌─────────────────┐
│    render()     │ Renderizado de gráficos
└───────┬─────────┘
        ▼
┌─────────────────┐
│  clock.tick()   │ Control de FPS
└─────────────────┘
```

## Métodos Principales

### Constructor y Configuración

```python
def __init__(self, width, height, title="Game", fps=60)
```

**Propósito**: Inicializar el motor con la configuración básica.

**Parámetros**:

- `width`: Ancho de la ventana
- `height`: Alto de la ventana
- `title`: Título de la ventana
- `fps`: Frames por segundo objetivo

**Operaciones**:

- Inicializa Pygame
- Configura la ventana del juego
- Crea el ObjectsManager
- Inicializa variables de control (running, paused, etc.)

### Gestión del Bucle Principal

```python
def run(self)
```

**Propósito**: Ejecutar el bucle principal del juego.

**Flujo**:

1. Llama a `init_game()` para inicialización específica
2. Mientras `running` sea True:
   - Controla FPS con `clock.tick()`
   - Llama a `handle_events()`
   - Si no está pausado:
     - Llama a `update()`
     - Llama a `render()`
3. Al finalizar, llama a `cleanup()`

### Manejo de Eventos

```python
def handle_events(self)
```

**Propósito**: Procesar eventos de Pygame y llamar a manejadores específicos.

**Operaciones**:

- Procesa eventos base (QUIT, F3 para debug)
- Llama a `on_handle_event(event)` para eventos específicos
- Llama a `on_handle_inputs()` para entradas continuas

### Actualización de Lógica

```python
def update(self)
```

**Propósito**: Actualizar todos los objetos y la lógica del juego.

**Operaciones**:

- Actualiza todos los objetos registrados
- Detecta colisiones entre objetos
- Llama a `on_update()` para lógica específica

### Renderizado

```python
def render(self)
```

**Propósito**: Renderizar todos los elementos visuales del juego.

**Operaciones**:

- Limpia la pantalla
- Llama a `on_render_background()` para fondo específico
- Dibuja todos los objetos registrados
- Dibuja hitboxes si el modo debug está activado
- Llama a `on_render_foreground()` para elementos de UI
- Actualiza la pantalla

## Sistema de Eventos Personalizado

```python
def emit_event(self, event_type, data=None, target_type=None)
```

**Propósito**: Emitir eventos personalizados a los objetos del juego.

**Parámetros**:

- `event_type`: Tipo de evento a emitir
- `data`: Datos asociados al evento (opcional)
- `target_type`: Tipo de objeto al que dirigir el evento (opcional)

**Operaciones**:

1. Intenta manejar el evento en el propio juego (métodos `on_*`)
2. Propaga el evento a los objetos registrados

## Gestión de Objetos

```python
def register_object(self, game_object)
```

**Propósito**: Registrar un objeto para que sea actualizado y renderizado automáticamente.

**Parámetros**:

- `game_object`: Objeto derivado de GameObject

**Operaciones**:

- Asigna el juego al objeto
- Añade el objeto a la lista de objetos gestionados

```python
def unregister_object(self, game_object)
```

**Propósito**: Eliminar un objeto del registro automático.

**Parámetros**:

- `game_object`: Objeto derivado de GameObject

**Operaciones**:

- Elimina el objeto de la lista de objetos gestionados

## Métodos para Sobrescribir (Hooks)

Estos métodos están destinados a ser sobrescritos por las clases derivadas:

```python
def init_game(self)
```

**Propósito**: Inicializar recursos específicos del juego.

```python
def on_update(self)
```

**Propósito**: Implementar lógica de actualización específica.

```python
def on_render_background(self)
```

**Propósito**: Renderizar elementos de fondo específicos.

```python
def on_render_foreground(self)
```

**Propósito**: Renderizar elementos de UI o efectos en primer plano.

```python
def on_handle_event(self, event)
```

**Propósito**: Procesar eventos específicos.

```python
def on_handle_inputs(self)
```

**Propósito**: Procesar entradas continuas (teclado, mouse).

```python
def cleanup(self)
```

**Propósito**: Liberar recursos específicos al finalizar.

## Modos Especiales

### Modo Debug

El motor incluye un modo de depuración que muestra información útil para desarrolladores:

- Activación: Pulsar F3 durante la ejecución
- Características:
  - Muestra hitboxes de todos los objetos
  - Imprime información sobre objetos registrados
  - Muestra estadísticas en pantalla (si implementado)

### Modo Pausa

El juego puede ser pausado, deteniendo las actualizaciones pero manteniendo el renderizado:

```python
def toggle_pause(self)
```

**Propósito**: Alternar el estado de pausa del juego.

## Ejemplo de Uso

```python
class MyGame(GameEngine):
    def init_game(self):
        # Inicializar objetos del juego
        player = Player(100, 100)
        self.register_object(player)

    def on_update(self):
        # Lógica específica del juego

    def on_render_background(self):
        # Dibujar fondo

    def on_render_foreground(self):
        # Dibujar UI

# Crear y ejecutar el juego
game = MyGame(800, 600, "Mi Juego", 60)
game.run()
```

## Consideraciones de Rendimiento

- El motor controla automáticamente los FPS
- Los objetos son actualizados y renderizados sólo si están registrados
- El sistema de detección de colisiones es optimizado para reducir comprobaciones innecesarias
- El modo debug puede reducir el rendimiento cuando está activado
