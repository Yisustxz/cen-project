# HUD (Heads-Up Display)

La clase `HUD` (Heads-Up Display) representa la interfaz gráfica que muestra información relevante al jugador durante el juego Space Shooter, como puntuación, vidas restantes, power-ups activos y mensajes de estado.

## Responsabilidades Principales

- **Mostrar puntuación** actual del jugador
- **Visualizar vidas** restantes con iconos
- **Indicar power-ups activos** y su duración
- **Mostrar mensajes** de estado del juego
- **Gestionar pantallas** de pausa y game over
- **Actualizar información** en tiempo real

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
|        HUD        |
+-------------------+
| - player          |
| - score_text      |
| - life_icon       |
| - powerup_icons   |
| - messages        |
| - game_over_panel |
| ...               |
+-------------------+
| + update_score()  |
| + show_message()  |
| + show_game_over()|
| + draw_lives()    |
| ...               |
+-------------------+
```

## Atributos Principales

| Atributo          | Tipo    | Descripción                                       |
| ----------------- | ------- | ------------------------------------------------- |
| `player`          | Player  | Referencia al jugador para acceder a sus datos    |
| `score_text`      | Text    | Objeto de texto para mostrar la puntuación        |
| `life_icon`       | Surface | Imagen del icono de vida                          |
| `powerup_icons`   | dict    | Diccionario con iconos para cada tipo de power-up |
| `messages`        | list    | Lista de mensajes temporales a mostrar            |
| `game_over_panel` | Surface | Panel de game over                                |
| `pause_panel`     | Surface | Panel de pausa                                    |
| `font`            | Font    | Fuente principal para textos                      |
| `large_font`      | Font    | Fuente grande para títulos                        |

## Inicialización

```python
def __init__(self, player=None)
```

**Propósito**: Inicializar el HUD con referencia al jugador.

**Parámetros**:

- `player`: Referencia al objeto jugador (opcional)

**Operaciones**:

- Llamar al constructor de la clase padre
- Establecer referencia al jugador
- Inicializar objetos de texto, fuentes y superficie
- Cargar iconos para vidas y power-ups
- Configurar paneles para estados especiales (pausa, game over)

```python
def set_images(self, images)
```

**Propósito**: Establecer las imágenes para los diferentes elementos del HUD.

**Parámetros**:

- `images`: Diccionario con imágenes para cada elemento

**Operaciones**:

- Asignar iconos de vida
- Asignar iconos de power-ups
- Configurar paneles de estado

## Elementos del HUD

### Marcador de Puntuación

```python
def update_score(self)
```

**Propósito**: Actualizar el texto del marcador con la puntuación actual.

**Operaciones**:

- Obtener la puntuación del jugador
- Actualizar el texto mostrado
- Posicionar en la esquina superior izquierda

```python
# Actualizar texto de puntuación
if self.player:
    score = self.player.score
    self.score_text.set_text(f"SCORE: {score}")
```

### Indicador de Vidas

```python
def draw_lives(self, surface)
```

**Propósito**: Dibujar iconos representando las vidas restantes.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

- Obtener número de vidas del jugador
- Dibujar iconos en fila en la parte superior derecha
- Ajustar espaciado entre iconos

```python
# Dibujar iconos de vida
if self.player and self.life_icon:
    lives = self.player.lives
    for i in range(lives):
        x = self.screen_width - 50 - (i * 40)
        y = 20
        surface.blit(self.life_icon, (x, y))
```

### Indicadores de Power-Ups

```python
def draw_powerups(self, surface)
```

**Propósito**: Mostrar iconos de power-ups activos y su duración.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

- Verificar power-ups activos en el jugador
- Dibujar iconos con barra de progreso de duración
- Posicionar en la parte inferior de la pantalla

```python
# Dibujar power-ups activos
if self.player:
    active_powerups = []

    # Comprobar cada tipo de power-up
    if self.player.shield_remaining > 0:
        active_powerups.append(("shield", self.player.shield_remaining / 3.0))
    if self.player.rapid_fire > 0:
        active_powerups.append(("rapid_fire", self.player.rapid_fire / 8000.0))
    if self.player.speed_boost > 1.0:
        active_powerups.append(("speed", self.player.speed_boost_time / 12000.0))

    # Dibujar cada power-up activo
    for i, (powerup_type, progress) in enumerate(active_powerups):
        if powerup_type in self.powerup_icons:
            # Posición
            x = 20 + (i * 70)
            y = self.screen_height - 60

            # Dibujar icono
            surface.blit(self.powerup_icons[powerup_type], (x, y))

            # Dibujar barra de progreso
            bar_width = 60
            bar_height = 8
            bar_x = x
            bar_y = y + 40

            # Fondo de la barra
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

            # Progreso
            if progress > 0:
                progress_width = int(bar_width * progress)
                bar_color = (0, 255, 0) if progress > 0.5 else (255, 255, 0) if progress > 0.25 else (255, 0, 0)
                pygame.draw.rect(surface, bar_color, (bar_x, bar_y, progress_width, bar_height))
```

### Sistema de Mensajes

```python
def show_message(self, text, duration=3000, color=(255, 255, 255), size='medium')
```

**Propósito**: Mostrar un mensaje temporal en pantalla.

**Parámetros**:

- `text`: Texto del mensaje
- `duration`: Duración en milisegundos
- `color`: Color del texto
- `size`: Tamaño del texto ('small', 'medium', 'large')

**Operaciones**:

- Crear nueva entrada de mensaje con tiempo de expiración
- Aplicar formato según tamaño
- Añadir a la lista de mensajes activos

```python
# Crear nuevo mensaje
font_size = 24  # Por defecto, tamaño medio
if size == 'small':
    font_size = 18
elif size == 'large':
    font_size = 36

message = {
    'text': text,
    'font': pygame.font.SysFont(None, font_size),
    'color': color,
    'end_time': pygame.time.get_ticks() + duration,
    'alpha': 255  # Opacidad inicial
}

self.messages.append(message)
```

```python
def update_messages(self)
```

**Propósito**: Actualizar estado de mensajes (duración, fade-out).

**Operaciones**:

- Verificar tiempos de expiración
- Aplicar efecto de fade-out a mensajes próximos a expirar
- Eliminar mensajes expirados

```python
# Actualizar mensajes
current_time = pygame.time.get_ticks()
for message in self.messages[:]:
    # Tiempo restante
    remaining = message['end_time'] - current_time

    # Fade-out en los últimos 500ms
    if remaining < 500:
        message['alpha'] = int(255 * (remaining / 500.0))

    # Eliminar si ha expirado
    if current_time >= message['end_time']:
        self.messages.remove(message)
```

```python
def draw_messages(self, surface)
```

**Propósito**: Dibujar mensajes activos en pantalla.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

- Dibujar cada mensaje en el centro de la pantalla
- Aplicar transparencia según tiempo restante
- Apilar mensajes verticalmente

```python
# Dibujar mensajes activos
y_offset = self.screen_height // 3
for message in self.messages:
    # Renderizar texto con color y alpha
    text_color = message['color']
    text_alpha = message['alpha']
    text_surface = message['font'].render(message['text'], True, text_color)

    # Aplicar transparencia
    if text_alpha < 255:
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, text_alpha))
        text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Centrar y dibujar
    x = (self.screen_width - text_surface.get_width()) // 2
    surface.blit(text_surface, (x, y_offset))
    y_offset += text_surface.get_height() + 10
```

### Panel de Game Over

```python
def show_game_over(self, score)
```

**Propósito**: Mostrar el panel de fin de juego con puntuación final.

**Parámetros**:

- `score`: Puntuación final del jugador

**Operaciones**:

- Activar panel de game over
- Mostrar puntuación final
- Mostrar mensaje de reinicio

```python
# Configurar panel de game over
self.game_over_active = True
self.final_score = score

# Crear textos
self.game_over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
self.score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))
self.restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
```

```python
def draw_game_over(self, surface)
```

**Propósito**: Dibujar el panel de game over.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

- Dibujar fondo semitransparente
- Mostrar textos centrados
- Animar elementos

```python
# Dibujar panel semitransparente
overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 180))
surface.blit(overlay, (0, 0))

# Game Over
x = (self.screen_width - self.game_over_text.get_width()) // 2
y = self.screen_height // 3
surface.blit(self.game_over_text, (x, y))

# Puntuación
x = (self.screen_width - self.score_text.get_width()) // 2
y += 80
surface.blit(self.score_text, (x, y))

# Instrucciones de reinicio
x = (self.screen_width - self.restart_text.get_width()) // 2
y += 50
# Parpadeo del texto de reinicio
if (pygame.time.get_ticks() // 500) % 2:
    surface.blit(self.restart_text, (x, y))
```

### Panel de Pausa

```python
def show_pause(self)
```

**Propósito**: Mostrar el panel de pausa del juego.

**Operaciones**:

- Activar panel de pausa
- Mostrar mensajes de control

```python
def draw_pause(self, surface)
```

**Propósito**: Dibujar el panel de pausa.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

- Dibujar fondo semitransparente
- Mostrar título "PAUSA"
- Mostrar controles e instrucciones

```python
# Dibujar panel semitransparente
overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 150))
surface.blit(overlay, (0, 0))

# Título
pause_text = self.large_font.render("PAUSA", True, (255, 255, 255))
x = (self.screen_width - pause_text.get_width()) // 2
y = self.screen_height // 3
surface.blit(pause_text, (x, y))

# Instrucciones
instructions = [
    "P - Continuar juego",
    "ESC - Salir",
    "D - Modo Debug " + ("ON" if self.debug_mode else "OFF")
]

y += 80
for instruction in instructions:
    text = self.font.render(instruction, True, (200, 200, 200))
    x = (self.screen_width - text.get_width()) // 2
    surface.blit(text, (x, y))
    y += 30
```

## Ciclo de Vida

### Actualización

```python
def on_update(self)
```

**Propósito**: Actualizar el estado del HUD en cada frame.

**Operaciones**:

1. Actualizar marcador de puntuación
2. Gestionar mensajes temporales
3. Actualizar estado de paneles especiales

### Renderizado

```python
def on_render(self, surface)
```

**Propósito**: Renderizar todos los elementos del HUD.

**Parámetros**:

- `surface`: Superficie donde dibujar

**Operaciones**:

1. Dibujar marcador de puntuación
2. Dibujar indicador de vidas
3. Dibujar indicadores de power-ups activos
4. Dibujar mensajes temporales
5. Dibujar paneles especiales si están activos

## Sistema de Eventos

```python
def on_game_event(self, event_type, data=None)
```

**Propósito**: Manejar eventos del juego relevantes para el HUD.

**Parámetros**:

- `event_type`: Tipo de evento a manejar
- `data`: Datos asociados al evento (opcional)

**Eventos Manejados**:

- **"game_paused"**: Mostrar panel de pausa
- **"game_resumed"**: Ocultar panel de pausa
- **"game_over"**: Mostrar panel de game over
- **"powerup_collected"**: Mostrar mensaje de power-up recogido
- **"meteor_destroyed"**: Actualizar marcador de puntuación

```python
# Manejo de eventos
if event_type == "game_paused":
    self.show_pause()
elif event_type == "game_resumed":
    self.pause_active = False
elif event_type == "game_over":
    score = data.get("score", 0) if data else 0
    self.show_game_over(score)
elif event_type == "powerup_collected":
    powerup_type = data.get("type", "") if data else ""

    # Mostrar mensaje según tipo
    if powerup_type == "shield":
        self.show_message("¡Escudo activado!", color=(0, 200, 255))
    elif powerup_type == "rapid_fire":
        self.show_message("¡Disparo rápido!", color=(255, 0, 255))
    elif powerup_type == "extra_life":
        self.show_message("¡Vida extra!", color=(0, 255, 0))
    elif powerup_type == "speed":
        self.show_message("¡Velocidad aumentada!", color=(255, 255, 0))
```

## Ejemplo de Uso

```python
# En el método init_game de SpaceShooterGame
def init_game(self):
    # Inicializar jugador
    self.player = Player(PLAYER_START_X, PLAYER_START_Y)
    self.register_object(self.player)

    # Inicializar HUD
    self.hud = HUD(self.player)
    self.hud.set_images({
        'life_icon': self.resource_manager.get_image('life'),
        'powerup_shield': self.resource_manager.get_image('icon_shield'),
        'powerup_rapid_fire': self.resource_manager.get_image('icon_rapid_fire'),
        'powerup_life': self.resource_manager.get_image('icon_life'),
        'powerup_speed': self.resource_manager.get_image('icon_speed')
    })
    self.register_object(self.hud)

    # Mostrar mensaje inicial
    self.hud.show_message("¡Preparado para la batalla espacial!", size='large')
```

## Buenas Prácticas

1. **Legibilidad**: Textos claros y contraste adecuado para leer en movimiento
2. **No invasivo**: El HUD no debe obstaculizar la visibilidad del juego
3. **Feedback inmediato**: Actualización instantánea de puntuación y estados
4. **Diseño coherente**: Estilo visual acorde con la temática espacial
5. **Claridad de estado**: Indicadores intuitivos para power-ups y vidas
6. **Mensajes informativos**: Textos cortos y descriptivos
7. **Animaciones sutiles**: Efectos de fade para transiciones suaves
