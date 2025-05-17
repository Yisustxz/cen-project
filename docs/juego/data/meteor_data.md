# Datos de Meteoritos (MeteorData)

La clase `MeteorData` encapsula todas las configuraciones y propiedades de los diferentes tipos de meteoritos disponibles en el juego.

## Descripción General

`MeteorData` es una clase estática que proporciona:

- Definiciones de los tipos de meteoritos (tamaños, colores, propiedades)
- Métodos para obtener datos de meteoritos aleatorios o específicos
- Funcionalidad para cargar imágenes de meteoritos

Esta separación entre datos y comportamiento facilita:

1. Balancear el juego modificando características de los meteoritos
2. Añadir nuevos tipos de meteoritos sin modificar la lógica del juego
3. Mantener una coherencia visual y de comportamiento

## Tipos de Meteoritos

La clase define varios tipos de meteoritos, combinando:

- **Colores**: Marrón (brown) y Gris (grey)
- **Tamaños**: Grande (big), Mediano (medium), Pequeño (small), Diminuto (tiny)

Cada tipo tiene configuraciones específicas para:

| Propiedad            | Descripción                                  |
| -------------------- | -------------------------------------------- |
| speed_x_range        | Rango de velocidad horizontal                |
| speed_y_range        | Rango de velocidad vertical                  |
| hp                   | Puntos de vida (resistencia)                 |
| points               | Puntos que otorga al ser destruido           |
| rotation_speed_range | Rango de velocidad de rotación               |
| hitbox_padding       | Ajuste del tamaño de la caja de colisión     |
| images               | Lista de imágenes disponibles para este tipo |

## Estructura de Datos

```python
TYPES = {
    "brown_big": {
        "speed_x_range": (-1, 1),
        "speed_y_range": (1, 3),
        "hp": 3,
        "points": 100,
        "rotation_speed_range": (-3, 3),
        "hitbox_padding": -10,
        "images": ["brown_big_1.png", "brown_big_2.png"]
    },
    # Más tipos...
}
```

## Métodos Principales

### get_random_type()

```python
@classmethod
def get_random_type(cls):
    """Devuelve un tipo de meteorito aleatorio."""
    return random.choice(list(cls.TYPES.keys()))
```

Selecciona aleatoriamente uno de los tipos de meteoritos disponibles.

### get_type_data(meteor_type)

```python
@classmethod
def get_type_data(cls, meteor_type):
    """Obtiene los datos para un tipo específico de meteorito."""
    if meteor_type in cls.TYPES:
        return cls.TYPES[meteor_type]
    return cls.TYPES[cls.get_random_type()]
```

Obtiene los datos de configuración para un tipo específico de meteorito. Si el tipo no existe, devuelve un tipo aleatorio.

### get_random_data()

```python
@classmethod
def get_random_data(cls):
    """Obtiene datos para un tipo aleatorio de meteorito."""
    meteor_type = cls.get_random_type()
    return meteor_type, cls.TYPES[meteor_type]
```

Devuelve tanto el tipo como los datos para un meteorito aleatorio.

### load_meteor_image(resource_manager, meteor_type)

```python
@classmethod
def load_meteor_image(cls, resource_manager, meteor_type):
    """Carga y devuelve una imagen aleatoria para el tipo de meteorito."""
    data = cls.get_type_data(meteor_type)
    image_file = random.choice(data["images"])
    image_path = f"images/meteors/{image_file}"

    # Nombre único para la imagen en el resource manager
    image_name = f"meteor_{meteor_type}_{image_file}"

    # Cargar la imagen si no está ya cargada
    if not resource_manager.get_image(image_name):
        resource_manager.load_image(image_name, image_path)

    return resource_manager.get_image(image_name)
```

Carga una imagen aleatoria para el tipo de meteorito solicitado, utilizando el gestor de recursos del juego.

## Uso desde la Clase Meteor

La clase `Meteor` utiliza `MeteorData` de la siguiente manera:

```python
# En SpaceShooterGame.create_meteor()
meteor_type = MeteorData.get_random_type()
meteor_data = MeteorData.get_type_data(meteor_type)
meteor_img = MeteorData.load_meteor_image(self.resource_manager, meteor_type)
meteor = Meteor(meteor_img, meteor_type, meteor_data)
```

## Ventajas de este Diseño

1. **Centralización**: Todas las propiedades de meteoritos en un único lugar
2. **Flexibilidad**: Fácil adición de nuevos tipos o modificación de los existentes
3. **Desacoplamiento**: La lógica de juego no depende directamente de los detalles específicos de cada tipo
4. **Balanceo**: Facilita el ajuste de la dificultad del juego modificando valores
5. **Organización**: Código más limpio y mejor estructurado

## Extensiones Posibles

Esta estructura podría extenderse para incluir:

- Diferentes comportamientos según el tipo (algunos meteoritos podrían moverse en patrones especiales)
- Efectos visuales específicos para cada tipo
- Meteoritos especiales con propiedades únicas
