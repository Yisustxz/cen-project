"""Utilidades para mostrar texto en la pantalla."""
import pygame
from motor.resource_manager import ResourceManager

def write_text(surface, text, color, x, y, font_size=16, font_name=None):
    """Muestra texto centrado en una posición específica."""
    font = pygame.font.Font(pygame.font.get_default_font(), font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

class TextRenderer:
    """Clase para renderizar texto usando un ResourceManager."""
    
    def __init__(self, resource_manager):
        """
        Inicializa el renderizador de texto con un gestor de recursos.
        
        Args:
            resource_manager: Instancia de ResourceManager para obtener fuentes
        """
        self.resource_manager = resource_manager
        
    def render_text(self, surface, text, color, x, y, font_size=16, font_name="default"):
        """
        Renderiza texto en la superficie con una fuente específica.
        
        Args:
            surface: Superficie donde dibujar
            text: Texto a mostrar
            color: Color del texto (tupla RGB)
            x: Posición X del centro del texto
            y: Posición Y del centro del texto
            font_size: Tamaño de la fuente
            font_name: Nombre de la fuente previamente cargada
        """
        font = self.resource_manager.get_font(font_name, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)
