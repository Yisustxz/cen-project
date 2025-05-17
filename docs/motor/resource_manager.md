# ResourceManager (Gestor de Recursos)

El `ResourceManager` es un componente del motor encargado de cargar, almacenar y gestionar los recursos del juego, como imágenes, sonidos y fuentes. Este gestor centraliza el acceso a los recursos y optimiza su uso mediante caché.

## Responsabilidades Principales

- **Cargar y almacenar imágenes**
- **Escalar imágenes al tamaño deseado**
- **Proporcionar acceso centralizado a los recursos**
- **Evitar la carga duplicada de recursos**
- **Liberar recursos cuando ya no son necesarios**

## Diagrama de Clase

```
+------------------+
|  ResourceManager |
+------------------+
| - images         |
| - sounds         |
| - fonts          |
| - game           |
+------------------+
| + load_image()   |
| + get_image()    |
| + load_sound()   |
| + get_sound()    |
| + load_font()    |
| + get_font()     |
| + clear()        |
| ...              |
+------------------+
```

## Inicialización

```python
def __init__(self, game=None)
```

**Propósito**: Inicializar el gestor de recursos.

**Parámetros**:

- `game`: Referencia al juego principal (opcional)

**Operaciones**:

- Inicializa diccionarios vacíos para cada tipo de recurso
- Guarda la referencia al juego principal

## Gestión de Imágenes

### Carga de Imágenes

```python
def load_image(self, name, path, scale=None)
```

**Propósito**: Cargar una imagen desde el disco y almacenarla en memoria.

**Parámetros**:

- `name`: Identificador único para la imagen
- `path`: Ruta al archivo de imagen
- `scale`: Porcentaje de escala o tamaño específico (opcional)

**Operaciones**:

1. Busca la ruta completa del archivo
2. Carga la imagen usando pygame
3. Escala la imagen si se especifica
4. Almacena la imagen en el diccionario de imágenes

**Ejemplo**:

```python
# Cargar una imagen al 50% de su tamaño original
resource_manager.load_image('player', 'images/player.png', 50)

# Cargar una imagen con un tamaño específico de 64x64
resource_manager.load_image('enemy', 'images/enemy.png', (64, 64))

# Cargar una imagen sin escalar
resource_manager.load_image('background', 'images/background.png')
```

### Acceso a Imágenes

```python
def get_image(self, name)
```

**Propósito**: Obtener una imagen previamente cargada.

**Parámetros**:

- `name`: Identificador de la imagen

**Retorno**:

- La imagen solicitada o None si no existe

**Ejemplo**:

```python
# Obtener una imagen cargada previamente
player_img = resource_manager.get_image('player')
enemy_img = resource_manager.get_image('enemy')
```

## Gestión de Sonidos

### Carga de Sonidos

```python
def load_sound(self, name, path, volume=1.0)
```

**Propósito**: Cargar un efecto de sonido desde el disco.

**Parámetros**:

- `name`: Identificador único para el sonido
- `path`: Ruta al archivo de sonido
- `volume`: Volumen del sonido (0.0 a 1.0, opcional)

**Operaciones**:

1. Busca la ruta completa del archivo
2. Carga el sonido usando pygame
3. Ajusta el volumen si se especifica
4. Almacena el sonido en el diccionario de sonidos

**Ejemplo**:

```python
# Cargar un efecto de sonido
resource_manager.load_sound('explosion', 'sounds/explosion.wav')

# Cargar un efecto de sonido a la mitad de volumen
resource_manager.load_sound('shoot', 'sounds/shoot.wav', 0.5)
```

### Acceso a Sonidos

```python
def get_sound(self, name)
```

**Propósito**: Obtener un sonido previamente cargado.

**Parámetros**:

- `name`: Identificador del sonido

**Retorno**:

- El sonido solicitado o None si no existe

**Ejemplo**:

```python
# Obtener y reproducir un sonido
explosion_sound = resource_manager.get_sound('explosion')
if explosion_sound:
    explosion_sound.play()
```

## Gestión de Fuentes

### Carga de Fuentes

```python
def load_font(self, name, size, path=None)
```

**Propósito**: Cargar o crear una fuente para renderizar texto.

**Parámetros**:

- `name`: Identificador único para la fuente
- `size`: Tamaño de la fuente en puntos
- `path`: Ruta al archivo de fuente (opcional, usa la predeterminada si no se especifica)

**Operaciones**:

1. Si se proporciona una ruta, carga la fuente desde el archivo
2. Si no, usa la fuente predeterminada del sistema
3. Almacena la fuente en el diccionario de fuentes

**Ejemplo**:

```python
# Cargar una fuente personalizada
resource_manager.load_font('title', 36, 'fonts/arcade.ttf')

# Usar la fuente predeterminada del sistema
resource_manager.load_font('text', 16)
```

### Acceso a Fuentes

```python
def get_font(self, name, size=None)
```

**Propósito**: Obtener una fuente previamente cargada, o crearla si no existe.

**Parámetros**:

- `name`: Identificador de la fuente
- `size`: Tamaño de la fuente (opcional, solo si no existe la fuente)

**Retorno**:

- La fuente solicitada o una nueva fuente predeterminada

**Ejemplo**:

```python
# Obtener una fuente para renderizar texto
title_font = resource_manager.get_font('title')
text_surface = title_font.render("Game Over", True, (255, 0, 0))
```

## Limpieza de Recursos

```python
def clear(self)
```

**Propósito**: Liberar todos los recursos cargados.

**Operaciones**:

- Vacía todos los diccionarios de recursos

```python
def clear_images(self)
```

**Propósito**: Liberar solo las imágenes cargadas.

```python
def clear_sounds(self)
```

**Propósito**: Liberar solo los sonidos cargados.

```python
def clear_fonts(self)
```

**Propósito**: Liberar solo las fuentes cargadas.

## Funcionalidades Avanzadas

### Comprobación de Recursos

```python
def has_image(self, name)
```

**Propósito**: Comprobar si una imagen está cargada.

```python
def has_sound(self, name)
```

**Propósito**: Comprobar si un sonido está cargado.

```python
def has_font(self, name)
```

**Propósito**: Comprobar si una fuente está cargada.

### Búsqueda de Archivos

```python
def find_file(self, path)
```

**Propósito**: Encontrar la ruta completa de un archivo.

**Parámetros**:

- `path`: Ruta relativa al archivo

**Retorno**:

- Ruta completa al archivo o la ruta original si no se encuentra

**Operaciones**:

1. Busca el archivo en el directorio actual
2. Busca el archivo en el directorio de recursos
3. Busca el archivo en el directorio de la aplicación

## Ejemplo de Uso

```python
# Inicialización en el juego
def init_game(self):
    # Cargar recursos
    self.resource_manager.load_image('player', 'images/player.png', 50)
    self.resource_manager.load_image('enemy', 'images/enemy.png', 40)
    self.resource_manager.load_image('background', 'images/background.jpg')

    self.resource_manager.load_sound('shoot', 'sounds/shoot.wav')
    self.resource_manager.load_sound('explosion', 'sounds/explosion.wav')

    self.resource_manager.load_font('title', 36, 'fonts/arcade.ttf')
    self.resource_manager.load_font('text', 16)

    # Crear objetos del juego
    player_img = self.resource_manager.get_image('player')
    player = Player(100, 100, player_img)
    self.register_object(player)

# Uso durante el juego
def on_player_shoot(self):
    # Reproducir sonido
    shoot_sound = self.resource_manager.get_sound('shoot')
    if shoot_sound:
        shoot_sound.play()

# Renderizado
def on_render_foreground(self):
    # Mostrar texto con fuente cargada
    title_font = self.resource_manager.get_font('title')
    text_surface = title_font.render("Score: 1000", True, (255, 255, 255))
    self.game_window.blit(text_surface, (100, 50))
```

## Mejores Prácticas

1. **Cargar recursos al inicio del juego**: Para evitar tiempos de carga durante el juego
2. **Usar identificadores significativos**: Nombres claros para los recursos facilitan su gestión
3. **Reutilizar recursos comunes**: Evitar cargar varias veces la misma imagen con diferentes nombres
4. **Liberar recursos no utilizados**: Especialmente en juegos con muchos niveles o escenas
5. **Optimizar tamaños de imagen**: Escalar imágenes a su tamaño de uso para mejorar el rendimiento
6. **Organizar recursos por tipo**: Mantener imágenes, sonidos y fuentes en directorios separados

## Consideraciones Técnicas

1. **Formatos de imagen**: PNG es recomendado por su soporte de transparencia
2. **Formatos de sonido**: WAV es recomendado por su compatibilidad con Pygame
3. **Manejo de errores**: El gestor maneja graciosamente los errores al cargar recursos
4. **Caché automática**: Evita cargar el mismo recurso múltiples veces
5. **Optimización de memoria**: Escalar imágenes reduce el uso de memoria
