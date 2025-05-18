# Plan de Tareas MVV - Space Shooter Multijugador

Este documento divide el Plan MVV en tareas específicas para facilitar su implementación.

## Fase 1: Preparación de Entidades con IDs

### Tarea 1.1: Implementar Sistema de IDs para Entidades Existentes

**Objetivo:** Añadir sistema de IDs a todas las entidades del juego para permitir seguimiento en red.

**Archivos a modificar:**

- `src/space_shooter/entities/player.py`
- `src/space_shooter/entities/meteor.py`
- `src/space_shooter/entities/missile.py`
- `src/space_shooter/core/game.py` (método para generar IDs)

**Pasos:**

1. Añadir función `generate_id` a `SpaceShooterGame` para crear identificadores únicos:

```python
def generate_id(self, prefix="obj"):
    """Genera un ID único para objetos del juego."""
    import uuid
    return f"{prefix}_{str(uuid.uuid4())[:8]}"
```

2. Modificar la clase Player:

   - Añadir campo `id` y `player_id`
   - Inicializar con `self.id = self.player_id = 'local'` por defecto
   - Añadir método para establecer ID desde la red

3. Modificar la clase Meteor:

   - Añadir campo `id`
   - Modificar el método de creación para asignar ID único
   - Añadir método para establecer ID desde la red

4. Modificar la clase Missile:

   - Añadir campos `id` y `player_id`
   - Guardar referencia al jugador que lo disparó
   - Modificar el método de creación para asignar ID único

5. Modificar la creación de objetos en SpaceShooterGame:
   - Asignar IDs únicos a cada entidad al crearla

**Diagrama de relación:**

```
Player (id=player_X) --dispara--> Missile (id=missile_Y, player_id=player_X)
```

### Tarea 1.2: Implementar Clases para Entidades Remotas

**Objetivo:** Implementar clases para representar entidades controladas por otros jugadores.

**Archivos a crear:**

- `src/space_shooter/entities/other_player.py`
- `src/space_shooter/entities/other_missile.py`

**Pasos:**

1. Implementar clase OtherPlayer:

   - Similar a Player pero sin control por teclado
   - Añadir método update_position para actualizar desde red
   - Desactivar manejo autónomo de colisiones

2. Implementar clase OtherMissile:

   - Similar a Missile pero sin causar daño real
   - Configurar para mostrar efectos visuales pero no aplicar daño

3. Implementar método para crear entidades remotas en SpaceShooterGame:

```python
def create_other_player(self, player_id, player_name, x, y):
    other_player = OtherPlayer(x, y, player_id, player_name)
    # Establecer imágenes, mismo proceso que Player local
    return other_player

def create_other_missile(self, missile_id, player_id, x, y):
    other_missile = OtherMissile(x, y, missile_id, player_id)
    # Configurar igual que misiles locales
    return other_missile
```

## Fase 2: Implementación de Protobuf y gRPC

### Tarea 2.1: Definir y Generar Protobuf

**Objetivo:** Crear definiciones protobuf y generar código para cliente/servidor.

**Archivos a crear:**

- `proto/spaceshooter.proto`
- Script para generar código: `generate_proto.sh`

**Pasos:**

1. Crear archivo protobuf según diseño en new_plan_mpv.md
2. Crear script para generar código Python y Go
3. Ejecutar script y verificar archivos generados

### Tarea 2.2: Implementar Servidor Go Básico

**Objetivo:** Implementar servidor Go con funcionalidad básica.

**Archivos a crear:**

- `go-server/main.go`
- `go-server/networking/server.go`

**Pasos:**

1. Implementar código del servidor según el diseño de new_plan_mpv.md
2. Probar ejecución básica del servidor

## Fase 3: Implementación del Cliente Networking

### Tarea 3.1: Implementar NetworkingManager

**Objetivo:** Crear el componente que maneja la comunicación con el servidor.

**Archivos a crear:**

- `src/space_shooter/networking/networking_manager.py`

**Pasos:**

1. Implementar NetworkingManager según diseño en new_plan_mpv.md
2. Añadir métodos para notificar eventos al servidor
3. Añadir métodos para procesar eventos recibidos

### Tarea 3.2: Integrar NetworkingManager con SpaceShooterGame

**Objetivo:** Conectar el juego con el gestor de red.

**Archivos a modificar:**

- `src/space_shooter/core/game.py`

**Pasos:**

1. Añadir campo `networking` a SpaceShooterGame
2. Modificar método `__init__` para aceptar parámetro de modo multijugador
3. Añadir métodos para conectar y desconectar del servidor
4. Implementar callbacks para eventos de red

## Fase 4: Integración del Sistema de Eventos

### Tarea 4.1: Implementar Manejo de Colisiones en Red

**Objetivo:** Modificar el sistema de colisiones para trabajo en red.

**Archivos a modificar:**

- `src/space_shooter/core/game.py` (methods handle_collision, etc.)

**Pasos:**

1. Modificar `handle_collision` para notificar eventos en red
2. Implementar procesamiento de eventos de colisión remotos

### Tarea 4.2: Implementar Notificación de Estado de Jugador

**Objetivo:** Añadir actualización periódica de estado de jugador.

**Archivos a modificar:**

- `src/space_shooter/core/game.py` (método update)

**Pasos:**

1. Modificar método `update` para enviar posición del jugador
2. Añadir manejo del tiempo para enviar actualizaciones periódicas

## Fase 5: Modificaciones a la Interfaz de Usuario

### Tarea 5.1: Adaptar el Menú para Multijugador

**Objetivo:** Modificar el menú para soportar modo multijugador.

**Archivos a modificar:**

- `src/menu/__init__.py` o similar

**Pasos:**

1. Añadir opción para unirse a partida
2. Añadir campo para ingresar nombre de jugador
3. Añadir campo para IP/puerto del servidor

### Tarea 5.2: Implementar Sistema de Sala de Espera

**Objetivo:** Añadir pantalla de espera hasta tener suficientes jugadores.

**Archivos a crear/modificar:**

- `src/space_shooter/lobby.py` o similar

**Pasos:**

1. Crear pantalla de sala de espera
2. Mostrar jugadores conectados
3. Añadir botón para iniciar partida (solo host)

## Fase 6: Pruebas y Refinamiento

### Tarea 6.1: Pruebas de Integración

**Objetivo:** Verificar funcionamiento del multijugador.

**Pasos:**

1. Probar conexión de múltiples clientes
2. Verificar sincronización de entidades
3. Verificar colisiones y eventos
4. Identificar y corregir problemas

### Tarea 6.2: Optimización de Rendimiento

**Objetivo:** Mejorar el rendimiento del sistema multijugador.

**Pasos:**

1. Medir latencia y buscar mejoras
2. Optimizar frecuencia de actualizaciones
3. Implementar interpolación para movimientos más fluidos

## Próximos Pasos después del MVV

1. Implementar sistema de salas múltiples
2. Añadir persistencia de puntuaciones
3. Implementar validación básica en servidor para prevenir trampas
4. Añadir chat y otras características sociales
