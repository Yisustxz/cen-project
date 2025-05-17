# SpaceShooterGame

La clase `SpaceShooterGame` es la implementación principal del juego Space Shooter. Esta clase hereda de `GameEngine` y extiende su funcionalidad para implementar las mecánicas específicas del juego.

## Responsabilidades Principales

- **Inicialización del juego** (recursos, jugador, enemigos)
- **Creación y gestión de entidades** (meteoritos, misiles, power-ups)
- **Lógica específica del juego** (generación de enemigos, puntuación)
- **Manejo de eventos de juego** (colisiones, disparos, power-ups)
- **Renderizado de elementos específicos** (fondo, HUD, efectos)
- **Gestión del estado del juego** (pausa, game over, reinicio)

## Diagrama de Clase

```
+--------------------+
|   GameEngine       |
+--------------------+
         ▲
         │
         │ hereda de
         │
+--------------------+
|  SpaceShooterGame  |
+--------------------+
| - resource_manager |
| - hud              |
| - loop_ctr         |
| - gameover         |
+--------------------+
| + init_game()      |
| + create_meteor()  |
| + on_update()      |
| + on_meteor_destroyed() |
| + on_player_fire_missile() |
| + restart_game()   |
| + create_powerup() |
| ...                |
+--------------------+
```

## Inicialización

```python
def __init__(self)
```

**Propósito**: Inicializar el juego con la configuración básica.

**Operaciones**:

- Llamar al constructor de la clase padre con el tamaño de ventana y FPS
- Inicializar el gestor de recursos
- Inicializar el HUD
- Inicializar contadores y estados del juego

```python
def init_game(self)
```

**Propósito**: Inicializar recursos específicos del juego y crear objetos iniciales.

**Operaciones**:

1. Cargar imágenes (nave, meteoritos, fondo, etc.)
2. Configurar el jugador
3. Crear meteoritos iniciales

## Gestión de Entidades

### Creación de Meteoritos

```python
def create_meteor(self)
```

**Propósito**: Crear un meteorito y registrarlo en el motor.

**Operaciones**:

1. Seleccionar tipo de meteorito aleatoriamente (color, tamaño)
2. Cargar imagen correspondiente
3. Crear un objeto Meteor con la imagen seleccionada
4. Registrar el meteorito en el motor

**Características**:

- Los meteoritos tienen tamaño, velocidad y rotación aleatorios
- Los meteoritos pequeños son más rápidos y dan menos puntos
- Los meteoritos grandes son más lentos y dan más puntos

### Creación de Misiles

```python
def on_player_fire_missile(self, data)
```

**Propósito**: Manejar el evento de disparo de misil del jugador.

**Parámetros**:

- `data`: Datos del evento con la posición (x, y) desde donde disparar

**Operaciones**:

1. Crear un objeto Missile en la posición indicada
2. Registrar el misil en el motor
3. Notificar el disparo a otros objetos mediante evento

### Creación de Power-ups

```python
def create_powerup(self, x, y, powerup_type=None)
```

**Propósito**: Crear un power-up y registrarlo en el motor.

**Parámetros**:

- `x`: Posición X donde crear el power-up
- `y`: Posición Y donde crear el power-up
- `powerup_type`: Tipo específico de power-up (opcional)

**Operaciones**:

1. Crear un objeto PowerUp en la posición indicada
2. Registrar el power-up en el motor

## Eventos del Juego

### Destrucción de Meteoritos

```python
def on_meteor_destroyed(self, data)
```

**Propósito**: Manejar el evento de destrucción de un meteorito.

**Parámetros**:

- `data`: Datos del evento con puntos, posición (x, y) y referencia al meteorito

**Operaciones**:

1. Asignar puntos al jugador
2. Determinar si se genera un power-up (probabilidad aleatoria)
3. Si corresponde, crear un power-up en la posición del meteorito destruido

### Recolección de Power-ups

```python
def on_powerup_collected(self, data)
```

**Propósito**: Manejar el evento de recolección de un power-up.

**Parámetros**:

- `data`: Datos del evento con tipo y posición (x, y) del power-up

**Operaciones**:

- Registrar la recogida (para efectos visuales o sonoros)

## Ciclo del Juego

### Actualización

```python
def on_update(self)
```

**Propósito**: Realizar la actualización específica del juego en cada frame.

**Operaciones**:

1. Incrementar contador de frames
2. Generar nuevos meteoritos periódicamente según contador
3. Verificar si el juego ha terminado (vidas del jugador)
4. Si el juego termina, notificar a todos los objetos

### Renderizado

```python
def on_render_background(self)
```

**Propósito**: Renderizar el fondo del juego.

**Operaciones**:

- Dibujar el fondo estrellado (imagen de tiles)

```python
def on_render_foreground(self)
```

**Propósito**: Renderizar elementos en primer plano y UI.

**Operaciones**:

1. Dibujar efectos de daño del jugador
2. Renderizar HUD (normal o game over según estado)

## Gestión del Estado del Juego

### Game Over

El estado de game over se controla mediante la variable `gameover`:

- Se activa cuando el jugador pierde todas sus vidas
- Detiene la generación de nuevos meteoritos
- Muestra una pantalla de game over
- Permite reiniciar el juego o salir

### Reinicio del Juego

```python
def restart_game(self)
```

**Propósito**: Reiniciar el juego para una nueva partida.

**Operaciones**:

1. Limpiar todos los objetos existentes
2. Reiniciar el jugador (posición, vidas)
3. Crear nuevos meteoritos iniciales
4. Reiniciar contadores y estado de juego

### Manejo de Eventos

```python
def on_handle_event(self, event)
```

**Propósito**: Procesar eventos específicos del juego.

**Operaciones**:

- En game over, procesar teclas Y (reiniciar) o N (salir)

```python
def on_handle_inputs(self)
```

**Propósito**: Gestionar entradas continuas del teclado.

**Operaciones**:

- Si el juego no está en game over, pasar el control de entrada al jugador

## Limpieza de Recursos

```python
def cleanup(self)
```

**Propósito**: Liberar recursos antes de cerrar el juego.

**Operaciones**:

1. Limpiar todos los objetos del juego
2. Liberar recursos del gestor de recursos

## Ejemplo de Flujo de Juego

```
1. Inicialización
   - Carga de recursos
   - Creación del jugador
   - Creación de meteoritos iniciales

2. Bucle del juego (cada frame)
   - Manejo de eventos (movimiento, disparo)
   - Generación de meteoritos según temporizador
   - Actualización de todos los objetos
   - Detección y manejo de colisiones
   - Renderizado del fondo
   - Renderizado de objetos
   - Renderizado del HUD

3. Colisiones
   - Jugador-Meteorito: El jugador pierde vida
   - Misil-Meteorito: El meteorito se destruye y da puntos
   - Jugador-PowerUp: El jugador obtiene beneficios

4. Game Over
   - Se muestra pantalla de Game Over
   - Se espera entrada del usuario para reiniciar o salir
```

## Extensión y Personalización

La clase `SpaceShooterGame` está diseñada para ser fácilmente extensible:

1. Añadir nuevos tipos de enemigos: Crear nuevas clases de entidades
2. Añadir nuevos power-ups: Extender los tipos en la clase PowerUp
3. Añadir niveles: Implementar una máquina de estados para diferentes niveles
4. Añadir jefes: Crear entidades específicas con comportamiento complejo
5. Mejorar efectos visuales: Extender los métodos de renderizado
