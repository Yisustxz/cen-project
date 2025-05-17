"""Constantes del juego."""
import pygame
from config import Config

# Dimensiones de la ventana cargadas desde la configuración
GAME_WIDTH = Config.get_screen_width()
GAME_HEIGHT = Config.get_screen_height()
SCREEN_SIZE = (GAME_WIDTH, GAME_HEIGHT)

# Colores
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (200, 200, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Colores semitransparentes (RGBA)
TRANS_BLACK = (0, 0, 0, 128)
TRANS_RED = (200, 0, 0, 128)
TRANS_GREEN = (0, 200, 0, 128)
TRANS_BLUE = (0, 0, 200, 128)

# Configuración del jugador
PLAYER_START_X = GAME_WIDTH // 2
PLAYER_START_Y = GAME_HEIGHT - 50
PLAYER_LIVES = 3
PLAYER_SPEED = 2

# Configuración de misiles
MISSILE_COOLDOWN = 200
MISSILE_SPEED = 5

# FPS del juego
FPS = 120

# Frecuencia de generación de meteoros
METEOR_SPAWN_FREQUENCY = 100

# Nombre del juego
GAME_TITLE = "Space Shooter" 