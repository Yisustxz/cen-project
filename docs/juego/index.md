# Documentación del Juego Space Shooter

Este directorio contiene la documentación detallada sobre la implementación específica del juego Space Shooter, que se construye sobre el motor documentado en la sección anterior.

## Índice

1. [Estructura del Juego](estructura.md)
2. [Implementación Principal (Game)](game.md)
3. [Entidades](entidades/index.md)
   - [Player](entidades/player.md)
   - [Meteor](entidades/meteor.md)
   - [Missile](entidades/missile.md)
4. [Interfaz de Usuario](ui/index.md)
   - [HUD](ui/hud.md)
   - [Sistema de Texto](ui/text.md)
5. [Datos del Juego](data/index.md)
   - [Datos de Meteoritos](data/meteor_data.md)
6. [Constantes y Configuración](constantes.md)
7. [Sistema de Eventos](eventos.md)
8. [Mecánicas del Juego](mecanicas.md)

## Descripción General

Space Shooter es un juego de disparos en 2D donde el jugador controla una nave espacial y debe evitar o destruir meteoritos que vuelan a través de la pantalla. El juego incluye un sistema de puntuación y múltiples vidas.

## Tecnologías Utilizadas

- **Motor de juego**: Motor propio basado en Pygame
- **Gráficos**: Sprites 2D
- **Detección de colisiones**: Sistema basado en hitboxes rectangulares
- **Estructuras de datos**: Colecciones estándar de Python

## Diagrama de Componentes

```
┌───────────────────────────────────────────────┐
│ SpaceShooterGame                              │
├───────────────────────────────────────────────┤
│           ┌───────┐         ┌───────┐         │
│           │ Player│         │ Meteor│         │
│           └───────┘         └───────┘         │
│                                               │
│           ┌───────┐         ┌───────┐         │
│           │Missile│         │MeteorData│      │
│           └───────┘         └───────┘         │
│                                               │
│           ┌───────┐         ┌───────┐         │
│           │  HUD  │         │ Text  │         │
│           └───────┘         └───────┘         │
│                                               │
└───────────────────────────────────────────────┘
```

## Flujo del Juego

1. **Inicialización**: Carga de recursos, creación del jugador y meteoritos iniciales
2. **Bucle Principal**:
   - Manejo de eventos (teclado, ratón)
   - Actualización de objetos (movimiento, colisiones)
   - Generación de nuevos meteoritos
   - Renderizado (fondo, objetos, UI)
3. **Finalización**: Manejo de Game Over, reinicio o salida

## Mecánicas Principales

- **Movimiento del jugador**: Controles laterales (izquierda/derecha)
- **Disparo de misiles**: Pulsando la barra espaciadora
- **Colisiones**: Perder vidas al chocar con meteoritos
- **Puntuación**: Ganar puntos por destruir meteoritos

Consulta los documentos individuales para obtener información detallada sobre cada componente del juego.
