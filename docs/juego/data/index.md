# Datos del Juego Space Shooter

Este directorio contiene la documentación detallada sobre las estructuras de datos utilizadas en el juego Space Shooter.

## Índice

1. [Datos de Meteoritos](meteor_data.md)

## Descripción General

Las estructuras de datos del juego están diseñadas para almacenar las configuraciones y propiedades de diferentes elementos del juego de manera organizada y fácilmente accesible.

## Características Principales

- **Encapsulación de datos**: Separación clara entre datos y comportamiento
- **Configuración centralizada**: Todos los parámetros en un solo lugar
- **Facilidad para balancear el juego**: Modificación rápida de valores como velocidades y puntos
- **Extensibilidad**: Posibilidad de añadir nuevos tipos de elementos fácilmente

## Diagrama de Módulos

```
┌─────────────────────────────────────────┐
│ space_shooter.data                      │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────┐                    │
│  │   MeteorData    │                    │
│  ├─────────────────┤                    │
│  │ - TYPES         │                    │
│  │ + get_random_type│                   │
│  │ + get_type_data │                    │
│  │ + get_random_data│                   │
│  │ + load_meteor_image│                 │
│  └─────────────────┘                    │
│                                         │
└─────────────────────────────────────────┘
```

Consulta los documentos individuales para obtener información detallada sobre cada estructura de datos.
