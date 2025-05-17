"""
Menú principal del juego Space Shooter.
Muestra las opciones para iniciar o unirse a una partida.
"""
import pygame
import sys
from enum import Enum

# Constantes de colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)
BLUE = (0, 0, 255)

# Constantes del menú
TITLE_FONT_SIZE = 48
OPTION_FONT_SIZE = 36
MENU_PADDING = 20
OPTION_SPACING = 20

class MenuOption(Enum):
    CREATE_GAME = 0
    JOIN_GAME = 1
    EXIT = 2

class MainMenu:
    """Clase que gestiona el menú principal del juego."""
    
    def __init__(self, screen):
        """
        Inicializa el menú principal.
        
        Args:
            screen: Superficie de pygame donde se dibujará el menú
        """
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        
        # Inicializar Pygame si no se ha hecho ya
        if not pygame.font.get_init():
            pygame.font.init()
        
        # Cargar fuentes
        self.title_font = pygame.font.SysFont("Arial", TITLE_FONT_SIZE, bold=True)
        self.option_font = pygame.font.SysFont("Arial", OPTION_FONT_SIZE)
        
        # Opciones del menú
        self.options = [
            "Crear partida",
            "Conectarse a partida", 
            "Salir"
        ]
        
        # Opción seleccionada actualmente (0-based index)
        self.selected_option = 0
        
        # Renderizar textos una vez
        self.title_text = self.title_font.render("Space Shooter Multiplayer", True, WHITE)
        self.option_texts = [self.option_font.render(option, True, WHITE) for option in self.options]
        self.selected_option_texts = [self.option_font.render(option, True, BLUE) for option in self.options]
    
    def handle_event(self, event):
        """
        Maneja eventos específicos del menú.
        
        Args:
            event: Evento de pygame a manejar
            
        Returns:
            MenuOption o None: La opción seleccionada o None si no se seleccionó ninguna
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                # Devolver la opción seleccionada
                if self.selected_option == 0:
                    return MenuOption.CREATE_GAME
                elif self.selected_option == 1:
                    return MenuOption.JOIN_GAME
                elif self.selected_option == 2:
                    return MenuOption.EXIT
        
        return None
    
    def render(self):
        """Renderiza el menú en la pantalla."""
        # Limpiar pantalla con color negro
        self.screen.fill(BLACK)
        
        # Dibujar título centrado
        title_x = (self.screen_width - self.title_text.get_width()) // 2
        title_y = self.screen_height // 4
        self.screen.blit(self.title_text, (title_x, title_y))
        
        # Dibujar opciones del menú
        option_y = self.screen_height // 2
        for i, option_text in enumerate(self.option_texts):
            # Determinar si esta opción está seleccionada
            text = self.selected_option_texts[i] if i == self.selected_option else self.option_texts[i]
            
            # Centrar horizontalmente
            option_x = (self.screen_width - text.get_width()) // 2
            
            # Dibujar texto
            self.screen.blit(text, (option_x, option_y))
            
            # Preparar la siguiente opción
            option_y += text.get_height() + OPTION_SPACING

def run_menu(screen):
    """
    Ejecuta el bucle principal del menú.
    
    Args:
        screen: Superficie de pygame donde se dibujará el menú
        
    Returns:
        MenuOption: Opción seleccionada por el usuario
    """
    menu = MainMenu(screen)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Manejar eventos específicos del menú
            result = menu.handle_event(event)
            if result is not None:
                return result
        
        # Renderizar menú
        menu.render()
        
        # Actualizar pantalla
        pygame.display.flip()
        
        # Limitar FPS
        clock.tick(60) 