"""Punto de entrada principal para el juego Space Shooter."""
import sys
import os
import pygame

# Agregar el directorio src al path para que Python pueda encontrar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ahora importar desde los módulos
import config
from space_shooter.core.game import SpaceShooterGame
from menu import MenuOption, run_menu
from space_shooter.core.constants import GAME_WIDTH, GAME_HEIGHT, GAME_TITLE

def init_pygame():
    """Inicializa Pygame y devuelve la pantalla."""
    pygame.init()
    
    # Aplicar configuración de pantalla completa si está habilitada
    display_flags = pygame.FULLSCREEN if config.Config.is_fullscreen() else 0
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), display_flags)
    pygame.display.set_caption(GAME_TITLE)
    return screen

def main(): 
    """Función principal del juego."""
    # Cargar configuración
    config.Config.load_config()
    
    # Verificar si debemos saltar el menú
    single_player_mode = config.Config.is_single_player_enabled()
    skip_menu_enabled = config.Config.should_skip_menu()
    
    # Inicializar pygame y obtener pantalla
    screen = init_pygame()
    
    # En modo single player con skipMenu activado, ir directamente al juego
    if single_player_mode and skip_menu_enabled:
        game = SpaceShooterGame()
        game.run()
        return

    # Mostrar el menú principal
    menu_result = run_menu(screen)

    try:
        # Manejar la opción seleccionada
        if menu_result == MenuOption.JOIN_GAME:
            # Configurar modo multijugador
            print("Iniciando modo multijugador...")
            
            # Activar modo multijugador sin valores por defecto
            # Si no hay configuración, fallará explícitamente
            config.Config.set(True, "frontend", "multiplayerMode", "enable")
            
            # Inicializar el juego
            # La conexión al servidor se maneja dentro de SpaceShooterGame
            game = SpaceShooterGame()
            game.run()
        elif menu_result == MenuOption.EXIT:
            print("Saliendo del juego...")
            pygame.quit()
            sys.exit()
    except Exception as e:
        print(f"Error al iniciar el juego: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
