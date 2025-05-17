# Text

La clase `Text` representa un elemento de texto que puede ser mostrado en pantalla en el juego Space Shooter. Proporciona funcionalidades para crear, posicionar, formatear y animar texto dinámico.

## Responsabilidades Principales

- **Renderizar texto** en pantalla con diferentes fuentes
- **Cambiar contenido** de forma dinámica
- **Aplicar efectos** como parpadeo, fade o cambio de color
- **Posicionar texto** de forma absoluta o relativa
- **Animar texto** para efectos visuales
- **Gestionar diferentes** tamaños y estilos

## Diagrama de Clase

```
+-------------------+
|     GameObject    |
+-------------------+
         ▲
         │
         │ hereda de
         │
+-------------------+
|        Text       |
+-------------------+
| - text            |
| - font            |
| - color           |
| - rendered_text   |
| - size            |
| - alignment       |
| - effects         |
| ...               |
+-------------------+
| + set_text()      |
| + set_color()     |
| + set_alignment() |
| + set_size()      |
| + apply_effect()  |
| ...               |
+-------------------+
```

## Atributos Principales

| Atributo            | Tipo    | Descripción                                      |
| ------------------- | ------- | ------------------------------------------------ |
| `text`              | str     | Contenido textual a mostrar                      |
| `font`              | Font    | Fuente utilizada para renderizar                 |
| `color`             | tuple   | Color RGB(A) del texto                           |
| `rendered_text`     | Surface | Superficie con el texto renderizado              |
| `size`              | int     | Tamaño de la fuente                              |
| `alignment`         | str     | Alineación del texto ('left', 'center', 'right') |
| `effects`           | dict    | Diccionario de efectos aplicados al texto        |
| `original_position` | tuple   | Posición original para efectos                   |

## Inicialización

```python
def __init__(self, x, y, text="", size=24, color=(255, 255, 255), font_name=None)
```

**Propósito**: Inicializar un objeto de texto con posición y propiedades.

**Parámetros**:

- `x`: Posición X inicial
- `y`: Posición Y inicial
- `text`: Contenido textual inicial (opcional)
- `size`: Tamaño de la fuente (opcional)
- `color`: Color RGB del texto (opcional)
- `font_name`: Nombre de la fuente a utilizar (opcional)

**Operaciones**:

- Llamar al constructor de la clase padre
- Inicializar atributos de texto y estilo
- Cargar la fuente especificada o usar la predeterminada
- Renderizar el texto inicial
- Configurar el rectángulo para posicionamiento

```python
# Inicialización de atributos
self.text = text
self.size = size
self.color = color
self.alignment = 'left'
self.effects = {}

# Cargar fuente
if font_name:
    try:
        self.font = pygame.font.Font(font_name, size)
    except:
        self.font = pygame.font.SysFont(None, size)
else:
    self.font = pygame.font.SysFont(None, size)

# Renderizar texto inicial
self._render_text()

# Configurar rectángulo
self.rect = self.rendered_text.get_rect()
self.rect.topleft = (x, y)
self.original_position = (x, y)
```

## Métodos Principales

### Cambio de Texto

```python
def set_text(self, text)
```

**Propósito**: Cambiar el contenido textual.

**Parámetros**:

- `text`: Nuevo texto a mostrar

**Operaciones**:

- Actualizar el atributo de texto
- Re-renderizar el texto
- Mantener la posición actual

```python
self.text = text
self._render_text()
old_pos = self.rect.topleft
self.rect = self.rendered_text.get_rect()
self.rect.topleft = old_pos
```

### Cambio de Apariencia

```python
def set_color(self, color)
```

**Propósito**: Cambiar el color del texto.

**Parámetros**:

- `color`: Nuevo color en formato RGB o RGBA

**Operaciones**:

- Actualizar el atributo de color
- Re-renderizar el texto

```python
def set_size(self, size)
```

**Propósito**: Cambiar el tamaño de la fuente.

**Parámetros**:

- `size`: Nuevo tamaño en puntos

**Operaciones**:

- Actualizar el atributo de tamaño
- Recrear el objeto de fuente
- Re-renderizar el texto

```python
def set_font(self, font_name)
```

**Propósito**: Cambiar la fuente utilizada.

**Parámetros**:

- `font_name`: Nombre o ruta de la nueva fuente

**Operaciones**:

- Intentar cargar la nueva fuente
- Recrear el objeto de fuente
- Re-renderizar el texto

### Posicionamiento

```python
def set_alignment(self, alignment)
```

**Propósito**: Establecer la alineación del texto.

**Parámetros**:

- `alignment`: Tipo de alineación ('left', 'center', 'right')

**Operaciones**:

- Actualizar el atributo de alineación
- Reposicionar el rectángulo según la alineación

```python
self.alignment = alignment
if alignment == 'center':
    self.rect.centerx = self.original_position[0]
elif alignment == 'right':
    self.rect.right = self.original_position[0]
else:  # left
    self.rect.left = self.original_position[0]
```

```python
def set_position(self, x, y)
```

**Propósito**: Cambiar la posición del texto.

**Parámetros**:

- `x`: Nueva posición X
- `y`: Nueva posición Y

**Operaciones**:

- Actualizar la posición del rectángulo
- Guardar la nueva posición original

### Efectos Visuales

```python
def apply_effect(self, effect_type, params=None)
```

**Propósito**: Aplicar un efecto visual al texto.

**Parámetros**:

- `effect_type`: Tipo de efecto ('blink', 'fade', 'wave', 'shadow', etc.)
- `params`: Parámetros específicos del efecto (opcional)

**Operaciones**:

- Registrar el efecto en el diccionario de efectos
- Configurar parámetros iniciales para el efecto

```python
# Efecto de parpadeo
if effect_type == 'blink':
    self.effects['blink'] = {
        'active': True,
        'interval': params.get('interval', 500) if params else 500,
        'start_time': pygame.time.get_ticks()
    }

# Efecto de desvanecimiento
elif effect_type == 'fade':
    self.effects['fade'] = {
        'active': True,
        'min_alpha': params.get('min_alpha', 50) if params else 50,
        'max_alpha': params.get('max_alpha', 255) if params else 255,
        'speed': params.get('speed', 5) if params else 5,
        'direction': 'down',
        'current_alpha': 255
    }

# Efecto de onda
elif effect_type == 'wave':
    self.effects['wave'] = {
        'active': True,
        'amplitude': params.get('amplitude', 5) if params else 5,
        'frequency': params.get('frequency', 0.1) if params else 0.1,
        'phase': 0
    }

# Efecto de sombra
elif effect_type == 'shadow':
    self.effects['shadow'] = {
        'active': True,
        'offset': params.get('offset', (2, 2)) if params else (2, 2),
        'color': params.get('color', (0, 0, 0)) if params else (0, 0, 0)
    }
```

```python
def remove_effect(self, effect_type)
```

**Propósito**: Eliminar un efecto visual aplicado.

**Parámetros**:

- `effect_type`: Tipo de efecto a eliminar

**Operaciones**:

- Eliminar el efecto del diccionario de efectos

### Renderizado Interno

```python
def _render_text(self)
```

**Propósito**: Renderizar el texto con la fuente y color actuales.

**Operaciones**:

- Crear una superficie con el texto renderizado
- Aplicar efectos como sombras si están activos
- Guardar la superficie resultante

```python
# Renderizado básico
self.rendered_text = self.font.render(self.text, True, self.color)

# Aplicar sombra si está activa
if 'shadow' in self.effects and self.effects['shadow']['active']:
    shadow_params = self.effects['shadow']
    shadow_surf = self.font.render(self.text, True, shadow_params['color'])

    # Crear superficie combinada
    combined = pygame.Surface((
        self.rendered_text.get_width() + abs(shadow_params['offset'][0]),
        self.rendered_text.get_height() + abs(shadow_params['offset'][1])
    ), pygame.SRCALPHA)

    # Dibujar sombra y luego texto
    shadow_pos = (
        max(0, shadow_params['offset'][0]),
        max(0, shadow_params['offset'][1])
    )
    text_pos = (
        max(0, -shadow_params['offset'][0]),
        max(0, -shadow_params['offset'][1])
    )

    combined.blit(shadow_surf, shadow_pos)
    combined.blit(self.rendered_text, text_pos)
    self.rendered_text = combined
```

## Ciclo de Vida

### Actualización

```python
def on_update(self)
```

**Propósito**: Actualizar el estado del texto en cada frame.

**Operaciones**:

1. Actualizar efectos activos
2. Reposicionar según efectos de animación
3. Actualizar propiedades visuales

```python
current_time = pygame.time.get_ticks()

# Efecto de parpadeo
if 'blink' in self.effects and self.effects['blink']['active']:
    blink = self.effects['blink']
    interval = blink['interval']
    self.visible = ((current_time - blink['start_time']) % (interval * 2)) < interval

# Efecto de desvanecimiento
if 'fade' in self.effects and self.effects['fade']['active']:
    fade = self.effects['fade']
    if fade['direction'] == 'down':
        fade['current_alpha'] -= fade['speed']
        if fade['current_alpha'] <= fade['min_alpha']:
            fade['current_alpha'] = fade['min_alpha']
            fade['direction'] = 'up'
    else:
        fade['current_alpha'] += fade['speed']
        if fade['current_alpha'] >= fade['max_alpha']:
            fade['current_alpha'] = fade['max_alpha']
            fade['direction'] = 'down'

# Efecto de onda
if 'wave' in self.effects and self.effects['wave']['active']:
    wave = self.effects['wave']
    wave['phase'] += wave['frequency']
    offset_y = int(math.sin(wave['phase']) * wave['amplitude'])
    self.rect.y = self.original_position[1] + offset_y
```

### Renderizado

```python
def on_render(self, surface)
```

**Propósito**: Renderizar el texto y sus efectos.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

1. Verificar visibilidad (para efectos de parpadeo)
2. Aplicar transparencia (para efectos de fade)
3. Dibujar el texto en la posición correcta

```python
# Solo dibujar si es visible
if not self.visible:
    return

# Aplicar transparencia si hay fade
if 'fade' in self.effects and self.effects['fade']['active']:
    alpha = self.effects['fade']['current_alpha']
    temp_surface = self.rendered_text.copy()
    temp_surface.set_alpha(alpha)
    surface.blit(temp_surface, self.rect)
else:
    # Dibujo normal
    surface.blit(self.rendered_text, self.rect)
```

## Ejemplos de Uso

### Texto Básico

```python
# Crear texto básico
score_text = Text(20, 20, "Score: 0", size=28, color=(255, 255, 255))
game.register_object(score_text)

# Actualizar dinámicamente
def update_score(new_score):
    score_text.set_text(f"Score: {new_score}")
```

### Texto con Efectos

```python
# Texto de game over con parpadeo
game_over = Text(400, 300, "GAME OVER", size=48, color=(255, 0, 0))
game_over.set_alignment('center')
game_over.apply_effect('blink', {'interval': 800})
game.register_object(game_over)

# Título con sombra
title = Text(400, 100, "SPACE SHOOTER", size=64, color=(0, 200, 255))
title.set_alignment('center')
title.apply_effect('shadow', {'offset': (3, 3), 'color': (0, 0, 100)})
game.register_object(title)

# Texto con desvanecimiento
instructions = Text(400, 400, "Presiona ESPACIO para comenzar", size=24)
instructions.set_alignment('center')
instructions.apply_effect('fade', {'min_alpha': 100, 'max_alpha': 255, 'speed': 3})
game.register_object(instructions)
```

### Texto Animado

```python
# Texto con ondulación
combo_text = Text(400, 200, "¡COMBO x3!", size=36, color=(255, 255, 0))
combo_text.set_alignment('center')
combo_text.apply_effect('wave', {'amplitude': 10, 'frequency': 0.15})
game.register_object(combo_text)

# Desactivar después de un tiempo
def on_combo_end():
    combo_text.remove_effect('wave')
    combo_text.set_color((150, 150, 150))
```

## Buenas Prácticas

1. **Legibilidad**: Elegir tamaños y colores que destaquen sobre el fondo
2. **Efectos sutiles**: Usar efectos para enfatizar sin ser excesivos
3. **Rendimiento**: Evitar re-renderizar texto innecesariamente
4. **Alineación coherente**: Mantener un sistema de alineación consistente
5. **Reutilización**: Reutilizar objetos de texto en lugar de crear nuevos
6. **Extensibilidad**: Implementar nuevos efectos de forma modular
7. **Internacionalización**: Permitir cambio de texto para diferentes idiomas
