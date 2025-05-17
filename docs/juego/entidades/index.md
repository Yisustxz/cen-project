# Entidades del Juego

Este directorio contiene la documentación detallada sobre las diferentes entidades que componen el juego Space Shooter.

## Resumen de Entidades

| Entidad               | Descripción            | Función Principal                                   |
| --------------------- | ---------------------- | --------------------------------------------------- |
| [Player](player.md)   | Nave del jugador       | Movimiento controlado por usuario, disparar misiles |
| [Meteor](meteor.md)   | Meteoritos que caen    | Obstáculos a evitar o destruir                      |
| [Missile](missile.md) | Proyectiles disparados | Destruir meteoritos                                 |
| [PowerUp](powerup.md) | Potenciadores          | Proporcionar beneficios al jugador                  |

## Jerarquía de Clases

Todas las entidades del juego heredan de la clase base `GameObject` del motor, que proporciona funcionalidad común:

```
           ┌────────────┐
           │ GameObject │
           └─────┬──────┘
                 │
      ┌──────────┼──────────┬────────────┐
      │          │          │            │
┌─────▼────┐┌────▼─────┐┌───▼────┐┌──────▼─────┐
│  Player  ││  Meteor  ││ Missile ││  PowerUp  │
└──────────┘└──────────┘└─────────┘└────────────┘
```

## Características Comunes

Todas las entidades comparten estas características heredadas de `GameObject`:

1. **Posición en pantalla** (`x`, `y`)
2. **Hitbox para colisiones**
3. **Visibilidad controlable**
4. **Rotación de sprites**
5. **Sistema de detección de colisiones**
6. **Respuesta a eventos del juego**

## Interacciones Entre Entidades

Las entidades interactúan entre sí principalmente a través de:

1. **Colisiones físicas**: Manejadas por el método `on_collide()`
2. **Eventos del juego**: Manejados por el método `on_game_event()`

### Ejemplos de Interacciones

- **Player ↔ Meteor**: El jugador pierde vida al chocar con un meteorito
- **Missile ↔ Meteor**: El misil destruye el meteorito y otorga puntos al jugador
- **Player ↔ PowerUp**: El jugador obtiene beneficios al recoger potenciadores

## Objetos Por Tipo

En el juego, las entidades se clasifican y gestionan según su tipo:

- **"player"**: La nave del jugador
- **"meteor"**: Meteoritos de diferentes tamaños y velocidades
- **"missile"**: Proyectiles disparados por el jugador
- **"powerup"**: Potenciadores con diferentes efectos

## Extensibilidad

El sistema de entidades está diseñado para ser fácilmente extensible:

1. **Nuevas entidades**: Crear una clase que herede de `GameObject`
2. **Comportamiento personalizado**: Implementar métodos `on_update()` y `on_collide()`
3. **Respuesta a eventos**: Implementar el método `on_game_event()`

Consulta los documentos individuales para obtener información detallada sobre cada entidad.
