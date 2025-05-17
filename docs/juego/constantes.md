# Constantes y Configuración

Este documento detalla las constantes y parámetros de configuración utilizados en Space Shooter, explicando su propósito, valores predeterminados y cómo afectan al comportamiento del juego.

## Estructura de Configuración

Las constantes del juego están organizadas por categorías y se definen principalmente en módulos específicos:

- `config.py`: Configuración general del juego
- `constants.py`: Constantes específicas del juego
- Archivos adicionales para configuraciones especializadas

## Configuración General

### Ventana y Visualización

```python
# Tamaño de la ventana
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Título del juego
GAME_TITLE = "Space Shooter"

# Configuración de FPS (frames por segundo)
TARGET_FPS = 60

# Modo pantalla completa
FULLSCREEN = False

# Tamaño de píxel base (para escalar elementos)
PIXEL_SIZE = 1  # Aumentar para juegos con estilo pixel art
```

### Rutas y Recursos

```python
# Carpetas de recursos
ASSETS_DIR = "assets"
IMAGES_DIR = f"{ASSETS_DIR}/images"
SOUNDS_DIR = f"{ASSETS_DIR}/sounds"
FONTS_DIR = f"{ASSETS_DIR}/fonts"

# Archivos de fuentes
MAIN_FONT = f"{FONTS_DIR}/space_font.ttf"
UI_FONT = f"{FONTS_DIR}/ui_font.ttf"

# Archivos de configuración
CONFIG_FILE = "config.json"
HIGHSCORE_FILE = "highscores.json"
```

## Constantes de Juego

### Jugador

```python
# Posición inicial del jugador
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - 100

# Características del jugador
PLAYER_SPEED = 5.0
PLAYER_LIVES = 3
PLAYER_MISSILE_COOLDOWN = 250  # ms entre disparos
PLAYER_INVINCIBILITY_TIME = 2000  # ms de invencibilidad tras daño
```

### Meteoritos

```python
# Generación de meteoritos
METEOR_SPAWN_RATE_INITIAL = 120  # frames entre generaciones (mayor = más lento)
METEOR_SPAWN_RATE_MIN = 30  # velocidad máxima de generación
METEOR_SPAWN_RATE_DECREASE = 0.01  # aceleración de la dificultad

# Propiedades de meteoritos por tamaño
METEOR_PROPERTIES = {
    'small': {
        'speed_min': 3.0,
        'speed_max': 4.0,
        'health': 1,
        'radius': 15,
        'score': 100,
        'spawn_chance': 0.3  # probabilidad relativa
    },
    'medium': {
        'speed_min': 1.5,
        'speed_max': 2.5,
        'health': 2,
        'radius': 25,
        'score': 200,
        'spawn_chance': 0.5
    },
    'large': {
        'speed_min': 1.0,
        'speed_max': 1.5,
        'health': 3,
        'radius': 40,
        'score': 300,
        'spawn_chance': 0.2
    }
}
```

### Misiles

```python
# Propiedades de misiles
MISSILE_SPEED = 7.0
MISSILE_DAMAGE = 1

# Propiedades de misiles mejorados (power-up)
ENHANCED_MISSILE_SPEED = 9.0
ENHANCED_MISSILE_DAMAGE = 2
```

### Power-ups

```python
# Probabilidad de generar power-up al destruir meteorito
POWERUP_SPAWN_CHANCE_BASE = 0.05
POWERUP_SPAWN_CHANCE_LARGE = 0.15
POWERUP_SPAWN_CHANCE_SMALL = 0.02

# Duración de los efectos (en milisegundos)
POWERUP_SHIELD_HITS = 3
POWERUP_RAPID_FIRE_DURATION = 8000
POWERUP_SPEED_DURATION = 12000

# Multiplicadores de efectos
POWERUP_RAPID_FIRE_MULTIPLIER = 0.3  # 30% del cooldown normal
POWERUP_SPEED_MULTIPLIER = 1.5  # 50% más rápido

# Tiempo de vida de los power-ups en pantalla
POWERUP_LIFETIME = 10000  # ms
```

### Sistema de Puntuación

```python
# Puntos por nivel de dificultad
DIFFICULTY_SCORE_MULTIPLIER = 1.0  # aumenta con el tiempo

# Puntos de bonificación
METEOR_STREAK_BONUS = 50  # puntos extra por destruir meteoritos consecutivamente
LEVEL_COMPLETION_BONUS = 1000  # puntos por completar un nivel
```

### Sistemas de Eventos

```python
# Eventos personalizados
PLAYER_DAMAGE_EVENT = "player_damage"
METEOR_DESTROYED_EVENT = "meteor_destroyed"
POWERUP_COLLECTED_EVENT = "powerup_collected"
GAME_OVER_EVENT = "game_over"
```

## Configuración Avanzada

### Dificultad Progresiva

```python
# Configuración de la progresión de dificultad
DIFFICULTY_INCREASE_RATE = 0.001  # incremento por frame
DIFFICULTY_MAX = 2.0  # multiplicador máximo de dificultad

# Eventos basados en dificultad
DIFFICULTY_THRESHOLDS = {
    0.5: "first_difficulty_increase",
    1.0: "second_difficulty_increase",
    1.5: "final_difficulty_increase"
}

# Efectos de la dificultad
def apply_difficulty(base_value, difficulty, mode='multiply'):
    """Aplica el factor de dificultad a un valor base"""
    if mode == 'multiply':
        return base_value * difficulty
    elif mode == 'divide':
        return base_value / max(difficulty, 0.1)
    elif mode == 'add':
        return base_value + (difficulty - 1.0) * base_value
    return base_value
```

### Sistema de Niveles

```python
# Configuración de niveles
LEVEL_METEOR_COUNT = 20  # meteoritos por nivel
LEVEL_BOSS_ENABLED = True  # habilitar jefes de nivel
LEVEL_BACKGROUND_CHANGE = True  # cambiar fondo por nivel
```

### Colores

```python
# Colores usados en el juego (formato RGB)
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),

    # Colores específicos del juego
    'shield': (0, 200, 255),
    'rapid_fire': (255, 0, 255),
    'speed_boost': (255, 255, 0),
    'extra_life': (0, 255, 0),
    'game_over': (255, 0, 0),
    'warning': (255, 100, 0),
    'score': (200, 200, 200)
}
```

## Debug y Desarrollo

```python
# Configuración de depuración
DEBUG_MODE = False
SHOW_FPS = False
SHOW_HITBOXES = False
INVINCIBLE_PLAYER = False  # para pruebas
SPAWN_ALL_POWERUPS = False  # para pruebas de power-ups
```

## Controles

```python
# Configuración de controles
CONTROLS = {
    'move_left': pygame.K_LEFT,
    'move_right': pygame.K_RIGHT,
    'fire': pygame.K_SPACE,
    'pause': pygame.K_p,
    'debug_toggle': pygame.K_d,
    'restart': pygame.K_r,
    'quit': pygame.K_ESCAPE
}
```

## Almacenamiento de Configuración

Las configuraciones pueden cargarse desde un archivo JSON para permitir su modificación sin recompilar:

```python
def load_config(config_file=CONFIG_FILE):
    """Carga la configuración desde un archivo JSON"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Archivo de configuración {config_file} no encontrado. Usando valores predeterminados.")
        return {}
    except json.JSONDecodeError:
        print(f"Error al decodificar el archivo de configuración {config_file}. Usando valores predeterminados.")
        return {}

def save_config(config, config_file=CONFIG_FILE):
    """Guarda la configuración en un archivo JSON"""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
```

## Ejemplo de Archivo de Configuración

```json
{
  "window": {
    "width": 800,
    "height": 600,
    "fullscreen": false,
    "fps": 60,
    "title": "Space Shooter"
  },
  "player": {
    "lives": 3,
    "speed": 5.0,
    "missile_cooldown": 250
  },
  "difficulty": {
    "increase_rate": 0.001,
    "max_difficulty": 2.0
  },
  "controls": {
    "move_left": "K_LEFT",
    "move_right": "K_RIGHT",
    "fire": "K_SPACE",
    "pause": "K_p"
  },
  "debug": {
    "enabled": false,
    "show_fps": false,
    "show_hitboxes": false
  }
}
```

## Uso de Constantes en el Código

### En el Juego Principal

```python
def init_game(self):
    # Inicializar jugador en posición predeterminada
    self.player = Player(PLAYER_START_X, PLAYER_START_Y)
    self.player.lives = PLAYER_LIVES
    self.player.missile_cooldown = PLAYER_MISSILE_COOLDOWN

    # Configurar generación de meteoritos
    self.meteor_spawn_rate = METEOR_SPAWN_RATE_INITIAL
    self.meteor_timer = 0

    # Inicializar dificultad
    self.difficulty = 1.0
```

### Para Calcular Valores Dinámicos

```python
def get_meteor_speed(self, size):
    """Calcula la velocidad de un meteorito basada en su tamaño y la dificultad actual"""
    props = METEOR_PROPERTIES[size]
    min_speed = props['speed_min']
    max_speed = props['speed_max']

    # Velocidad base aleatoria
    base_speed = random.uniform(min_speed, max_speed)

    # Aplicar factor de dificultad
    return apply_difficulty(base_speed, self.difficulty)
```

## Buenas Prácticas

1. **Centralización**: Mantener todas las constantes en archivos dedicados
2. **Nombres descriptivos**: Usar nombres claros y descriptivos en mayúsculas
3. **Comentarios**: Documentar el propósito y las unidades de cada constante
4. **Valores razonables**: Establecer valores iniciales equilibrados
5. **Configurabilidad**: Permitir modificaciones a través de archivos externos
6. **Categorización**: Agrupar constantes relacionadas
7. **Evitar números mágicos**: No usar valores numéricos directamente en el código
