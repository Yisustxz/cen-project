"""Sistema HUD (Heads-Up Display) para el juego."""
import pygame
from space_shooter.core.constants import WHITE, RED, GREEN
from config import Config

class HUD:
    """Clase para gestionar el HUD del juego."""
    
    def __init__(self, game):
        """
        Inicializa el HUD.
        
        Args:
            game: Referencia al juego principal
        """
        self.game = game
        self.font = pygame.font.Font(pygame.font.get_default_font(), 16)
        self.small_font = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.big_font = pygame.font.Font(pygame.font.get_default_font(), 24)
        
        # Obtener las dimensiones del juego y del nivel
        self.screen_width = Config.get_screen_width()
        self.screen_height = Config.get_screen_height()
        self.level_width = Config.get_level_width()
        self.level_height = Config.get_level_height()
        
        # Calcular factor de escala entre el nivel y la pantalla
        self.scale_x = self.screen_width / self.level_width
        self.scale_y = self.screen_height / self.level_height
        
    def render(self, game_window, level_surface, player, debug_mode=False):
        """
        Renderiza todo el HUD.
        
        Args:
            game_window: Ventana principal del juego donde dibujar
            level_surface: Superficie del nivel (ya renderizada)
            player: Objeto del jugador
            debug_mode: Si está activo el modo debug
        """
        # Escalar la superficie del nivel a la ventana real
        scaled_surface = pygame.transform.scale(level_surface, (self.screen_width, self.screen_height))
        game_window.blit(scaled_surface, (0, 0))
        
        # Mostrar vidas con iconos
        self.render_lives(game_window, player.lives)
        
        # Mostrar puntuación
        self.render_score(game_window, player.score)
        
        # En modo debug, mostrar información adicional
        if debug_mode:
            self.render_debug_info(game_window)
            
    def render_lives(self, surface, lives):
        """
        Renderiza las vidas del jugador con iconos.
        
        Args:
            surface: Superficie donde dibujar
            lives: Número de vidas
        """
        # Texto "Lives:"
        text_surface = self.font.render("Lives:", True, WHITE)
        surface.blit(text_surface, (20, 20))
        
        # Dibujar iconos de vida
        for i in range(lives):
            # Crear un pequeño rectángulo rojo para cada vida
            pygame.draw.rect(surface, RED, (90 + (i * 25), 20, 20, 20))
            # Agregar un borde blanco
            pygame.draw.rect(surface, WHITE, (90 + (i * 25), 20, 20, 20), 1)
    
    def render_score(self, surface, score):
        """
        Renderiza la puntuación.
        
        Args:
            surface: Superficie donde dibujar
            score: Puntuación actual
        """
        # Crear un fondo semitransparente para la puntuación
        score_bg = pygame.Surface((150, 30), pygame.SRCALPHA)
        score_bg.fill((0, 0, 0, 128))  # Negro semitransparente
        surface.blit(score_bg, (self.screen_width - 160, 15))
        
        # Texto formateado para la puntuación
        score_text = f"SCORE: {score:,}"
        text_surface = self.font.render(score_text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.right = self.screen_width - 20
        text_rect.top = 20
        surface.blit(text_surface, text_rect)
    
    def render_debug_info(self, surface):
        """
        Renderiza información de depuración.
        
        Args:
            surface: Superficie donde dibujar
        """
        # Obtener contadores de objetos
        player_count = self.game.count_objects_by_type("player")
        meteor_count = self.game.count_objects_by_type("meteor")
        missile_count = self.game.count_objects_by_type("missile")
        
        # Crear un panel semitransparente con información
        debug_bg = pygame.Surface((180, 100), pygame.SRCALPHA)
        debug_bg.fill((30, 30, 30, 200))  # Gris oscuro semitransparente
        surface.blit(debug_bg, (self.screen_width - 190, self.screen_height - 110))
        
        # Información de depuración
        debug_texts = [
            f"FPS: {self.game.clock.get_fps():.1f}",
            f"Objetos: {player_count + meteor_count + missile_count}",
            f"Jugadores: {player_count}",
            f"Meteoritos: {meteor_count}",
            f"Misiles: {missile_count}"
        ]
        
        # Renderizar textos
        for i, text in enumerate(debug_texts):
            text_surface = self.small_font.render(text, True, GREEN)
            surface.blit(text_surface, (self.screen_width - 180, self.screen_height - 100 + (i * 18)))
            
    def render_game_over(self, surface):
        """
        Renderiza la pantalla de game over.
        
        Args:
            surface: Superficie donde dibujar
        """
        # Fondo semitransparente
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Negro semitransparente
        surface.blit(overlay, (0, 0))
        
        # Mensaje de game over
        gameover_text = "GAME OVER"
        text_surface = self.big_font.render(gameover_text, True, RED)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.screen_width // 2, self.screen_height // 2 - 20)
        surface.blit(text_surface, text_rect)
        
        # Mensaje para continuar
        continue_text = "Press Y to play again or N to quit"
        text_surface = self.font.render(continue_text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.screen_width // 2, self.screen_height // 2 + 20)
        surface.blit(text_surface, text_rect) 