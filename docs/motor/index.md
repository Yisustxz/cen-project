# Documentación del Motor de Juego

Este directorio contiene la documentación detallada del motor de juego utilizado como base para Space Shooter.

## Índice

1. [Arquitectura del Motor](arquitectura.md)
2. [GameEngine](game_engine.md) - Motor de juego principal
3. [ObjectsManager](objects_manager.md) - Gestión de objetos del juego
4. [Sprite](sprite.md) - Sistema de sprites y objetos del juego
5. [ResourceManager](resource_manager.md) - Gestión de recursos
6. [Ciclo de Vida](ciclo_de_vida.md) - Explicación detallada del ciclo de vida
7. [Sistema de Eventos](eventos.md) - Sistema de propagación de eventos
8. [Sistema de Colisiones](colisiones.md) - Detección y manejo de colisiones
9. [Patrones de Diseño](patrones.md) - Patrones implementados en el motor

## Diagrama General

```
┌─────────────────────────────────────────┐
│ Juego Específico (SpaceShooterGame)     │
├─────────────────────────────────────────┤
│ Motor del Juego (GameEngine)            │
├─────────────────────────────────────────┤
│ Gestión de Objetos  │ Gestión Recursos  │
├─────────────────────┼───────────────────┤
│ Objetos del Juego (GameObject)          │
├─────────────────────────────────────────┤
│ Pygame                                  │
└─────────────────────────────────────────┘
```

## Modo de Uso

Este motor está diseñado para ser extendido mediante la creación de nuevas clases que hereden de las clases base:

1. Crea una clase que herede de `GameEngine` para implementar un juego específico
2. Crea clases que hereden de `GameObject` para implementar entidades específicas
3. Usa los métodos "on\_\*" para sobrescribir comportamientos sin alterar el flujo principal

Consulta los documentos individuales para obtener información detallada sobre cada componente.
