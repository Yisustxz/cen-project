# Meteorito (Meteor)

La clase `Meteor` representa los asteroides que el jugador debe evitar o destruir durante el juego.

## Descripción General

Los meteoritos son objetos que caen desde la parte superior de la pantalla hacia abajo con diferentes velocidades y patrones de movimiento. Existen varios tipos de meteoritos con diferentes características.

## Características Principales

- Diferentes tipos y tamaños basados en datos de `MeteorData`
- Movimiento aleatorio con componentes vertical y horizontal
- Rotación progresiva para efectos visuales
- Sistema de puntos de vida (HP) para determinar resistencia
- Efectos visuales al recibir daño (parpadeo)
- Recompensas en puntos al ser destruidos

## Constructor y Atributos

```python
def __init__(self, image, meteor_type, data=None):
    """
    Inicializa un nuevo meteorito.

    Args:
        image: Imagen del meteorito
        meteor_type: Tipo de meteorito (brown_big, grey_small, etc.)
        data: Diccionario con los datos de configuración (opcional)
    """
    # Inicialización en posición aleatoria en la parte superior
    x = random.randint(0, 800)
    y = -100

    # Inicialización básica como GameObject
    super().__init__(x, y, image, obj_type="meteor")

    # Propiedades específicas según el tipo
    self.meteor_type = meteor_type

    # Configurar según los datos proporcionados
    if data:
        speed_x_range = data.get("speed_x_range", (-1, 1))
        speed_y_range = data.get("speed_y_range", (1, 3))
        rotation_range = data.get("rotation_speed_range", (-3, 3))

        self.speed_x = random.uniform(speed_x_range[0], speed_x_range[1])
        self.speed_y = random.uniform(speed_y_range[0], speed_y_range[1])
        self.hp = data.get("hp", 1)
        self.points = data.get("points", 50)

        # Configurar rotación aleatoria
        rotation_speed = random.uniform(rotation_range[0], rotation_range[1])
        self.set_rotation(random.randint(0, 360), rotation_speed)

        # Crear hitbox ajustada
        padding = data.get("hitbox_padding", -5)
        self.create_hitbox(padding=padding)
    else:
        # Configuración de compatibilidad con código antiguo...
```

## Métodos Principales

### on_update()

Actualiza la posición y el estado del meteorito:

- Aplica el movimiento según velocidades
- Controla el efecto de parpadeo (blink)
- Verifica si ha salido de la pantalla para eliminarlo

### take_damage(damage=1)

Reduce los puntos de vida del meteorito y maneja efectos visuales:

- Resta puntos de vida (hp)
- Activa el parpadeo
- Si los puntos de vida llegan a cero:
  - Notifica la destrucción (evento `meteor_destroyed`)
  - Asigna los puntos
  - Se elimina a sí mismo

### on_collide(other_entity)

Maneja colisiones con otras entidades:

- Si colisiona con un misil, llama a `take_damage()`

### on_game_event(event_type, data)

Reacciona a eventos del juego:

- Al recibir evento `game_over`, detiene el movimiento

## Creación desde el Juego

Los meteoritos se crean utilizando la clase `MeteorData`:

```python
# En SpaceShooterGame.create_meteor()
meteor_type = MeteorData.get_random_type()
meteor_data = MeteorData.get_type_data(meteor_type)
meteor_img = MeteorData.load_meteor_image(self.resource_manager, meteor_type)
meteor = Meteor(meteor_img, meteor_type, meteor_data)
self.register_object(meteor)
```

## Flujo de Vida

1. **Creación**: Se instancia con tipo y propiedades aleatorias
2. **Movimiento**: Actualiza posición en cada frame
3. **Colisión**:
   - Con misiles: Recibe daño
   - Con el jugador: Causa daño al jugador
4. **Destrucción**:
   - Al quedarse sin puntos de vida
   - Al salir de la pantalla
   - Al finalizar el juego

## Tipos de Meteoritos

Los meteoritos tienen características según su tipo, definidas en `MeteorData`:

| Tipo         | Resistencia | Velocidad  | Puntos  |
| ------------ | ----------- | ---------- | ------- |
| brown_big    | 3 HP        | Lenta      | 100 pts |
| brown_medium | 2 HP        | Media      | 75 pts  |
| brown_small  | 1 HP        | Rápida     | 50 pts  |
| brown_tiny   | 1 HP        | Muy rápida | 25 pts  |
| grey_big     | 4 HP        | Muy lenta  | 120 pts |
| grey_medium  | 2 HP        | Media      | 80 pts  |
| grey_small   | 1 HP        | Rápida     | 60 pts  |
| grey_tiny    | 1 HP        | Muy rápida | 30 pts  |

## Interacciones

- **Con el jugador**: Causa daño al colisionar
- **Con misiles**: Recibe daño al colisionar
- **Con otros meteoritos**: Sin interacción (atraviesan)

## Consejos de Implementación

1. Priorizar la destrucción de meteoritos grandes primero por mayor puntaje
2. Los meteoritos grises son más resistentes que los marrones
3. Los meteoritos pequeños son más difíciles de golpear pero menos peligrosos
4. La velocidad horizontal varía, lo que hace impredecible su trayectoria
