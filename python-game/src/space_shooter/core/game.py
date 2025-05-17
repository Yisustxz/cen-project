"""Implementación del juego Space Shooter."""
import pygame
from pygame.locals import *
import random

# Usar importaciones absolutas en lugar de relativas
from motor.game_engine import GameEngine
from motor.resource_manager import ResourceManager
from space_shooter.entities.player import Player
from space_shooter.entities.meteor import Meteor
from space_shooter.entities.missile import Missile
from space_shooter.data.meteor_data import MeteorData
from space_shooter.core.meteor_manager import MeteorManager
from space_shooter.ui.text import write_text
from space_shooter.ui.hud import HUD
from space_shooter.utils.delta_time import DeltaTime
from space_shooter.core.constants import (
    PLAYER_START_X, PLAYER_START_Y,
    FPS, METEOR_SPAWN_FREQUENCY, GAME_TITLE
)
from config import Config

class SpaceShooterGame(GameEngine):
    """Implementación específica del juego Space Shooter."""

    def __init__(self):
        """Inicializa el juego."""
        print("Inicializando SpaceShooterGame...")
        # Llamar al constructor de la clase padre con la configuración básica
        width = Config.get_screen_width()
        height = Config.get_screen_height()
        super().__init__(width, height, GAME_TITLE, FPS)

        # Inicializar gestor de recursos con referencia al juego
        self.resource_manager = ResourceManager(game=self)
        
        # Inicializar el gestor de meteoritos
        self.meteor_manager = MeteorManager(self)
        
        # Inicializar el HUD con referencia al juego
        self.hud = HUD(self)

        # Contadores específicos del juego
        self.loop_ctr = 0
        self.gameover = False
                
        # Asegurarnos de que DeltaTime está inicializado
        DeltaTime.init()
        
        print("SpaceShooterGame inicializado correctamente.")

    def init_game(self):
        """Inicializa los recursos específicos del juego."""
        print("Inicializando recursos del juego...")
        try:
            # Cargar imágenes
            print("Cargando imágenes...")
            self.resource_manager.load_image('spaceship', 'images/spaceship.png', 40)
            self.resource_manager.load_image('damage', 'images/damage.png', 80)
            self.resource_manager.load_image('background', 'images/background1.png')

            # Configurar las imágenes del jugador
            print("Configurando jugador...")
            spaceship_img = self.resource_manager.get_image('spaceship')
            damage_img = self.resource_manager.get_image('damage')

            # Inicializar el jugador
            level_width = Config.get_level_width()
            player_x = level_width // 2  # Centrar el jugador en el nivel virtual
            player_y = Config.get_level_height() - 50  # Colocar cerca del borde inferior
            player = Player(player_x, player_y)
            player.set_images(spaceship_img, damage_img)
            
            # Registrar el jugador en el motor
            self.register_object(player)

            # Crear el primer meteorito
            print("Creando meteorito inicial...")
            self.meteor_manager.create_meteor()
            print("Recursos del juego inicializados correctamente.")
        except Exception as e:
            print(f"Error al inicializar recursos: {e}")
            import traceback
            traceback.print_exc()
            self.quit()

    def on_handle_event(self, event):
        """Procesa eventos específicos del juego."""
        if self.gameover and event.type == pygame.KEYDOWN:
            if event.key == K_y:
                print("Reiniciando juego...")
                self.restart_game()
            elif event.key == K_n:
                print("Saliendo del juego...")
                self.quit()

    def on_handle_inputs(self):
        """Gestiona entradas continuas del usuario."""
        # Si el juego está en curso, manejar las entradas específicas
        if not self.gameover:
            keys = pygame.key.get_pressed()
            
            # Obtener el jugador y dejar que maneje sus propias entradas
            players = self.objects_manager.get_objects_by_type("player")
            if players:
                players[0].handle_input(keys)

    def on_player_fire_missile(self, data):
        """
        Maneja el evento de disparo de misil del jugador.
        
        Args:
            data: Datos del evento con la posición (x, y) desde donde disparar
        """
        if 'x' in data and 'y' in data:
            missile = Missile(data['x'], data['y'])
            # Registrar el misil en el motor
            self.register_object(missile)
            # Notificar el disparo a otros objetos
            self.emit_event("missile_fired", {"x": data['x'], "y": data['y']})

    def on_update(self):
        """Actualización específica del juego (llamada por el motor)."""
        # No actualizar si estamos en game over
        if self.gameover:
            return

        # Actualizar gestor de meteoritos
        self.meteor_manager.update()

        # Verificar si el juego ha terminado
        player = self.objects_manager.get_objects_by_type("player")[0]
        if player.lives <= 0:
            print("¡Juego terminado! Vidas agotadas.")
            self.gameover = True
            # Notificar a todos los objetos del fin del juego
            self.emit_event("game_over")

    def on_meteor_destroyed(self, data):
        """
        Maneja el evento de destrucción de un meteorito.
        
        Args:
            data: Datos del evento con points, x, y, y meteor
        """
        if 'points' in data and 'x' in data and 'y' in data:
            # Asignar puntos al jugador
            players = self.objects_manager.get_objects_by_type("player")
            if players:
                players[0].add_score(data['points'])
                
            # Notificar al gestor de meteoritos
            self.meteor_manager.on_meteor_destroyed(data)

    def on_render_background(self, surface):
        """
        Renderiza el fondo del juego en la superficie virtual.
        
        Args:
            surface: Superficie virtual donde dibujar el fondo
        """
        # Dibujar el fondo en la superficie del nivel
        bg = self.resource_manager.get_image('background')
        level_width = Config.get_level_width()
        level_height = Config.get_level_height()
        
        for bg_x in range(0, level_width, bg.get_width()):
            for bg_y in range(0, level_height, bg.get_height()):
                surface.blit(bg, (bg_x, bg_y))

    def on_render_foreground(self, surface):
        """
        Renderiza elementos en primer plano en la superficie virtual.
        
        Args:
            surface: Superficie virtual donde dibujar
        """
        # Obtener el jugador
        player = self.objects_manager.get_objects_by_type("player")[0]
        
        # Dibujar daño si el jugador ha sido golpeado
        player.draw_damage(surface)

    def render(self):
        """
        Sobrescribir el método render para manejar el HUD en la ventana real.
        """
        # Usar la implementación base para dibujar juego y objetos en la superficie virtual
        self.game_surface.fill((0, 0, 0))
        self.on_render_background(self.game_surface)
        self.objects_manager.draw_objects(self.game_surface)
        self.on_render_foreground(self.game_surface)
        
        if self.debug_mode:
            self.objects_manager.draw_hitboxes(self.game_surface)
        
        # Renderizar el HUD, pasando la superficie virtual para que la escale
        if self.gameover:
            # Escalar la superficie virtual y dibujarla en la ventana
            scaled_surface = pygame.transform.scale(self.game_surface, self.screen_size)
            self.game_window.blit(scaled_surface, (0, 0))
            # Mostrar pantalla de game over
            self.hud.render_game_over(self.game_window)
        else:
            # Usar el HUD para mostrar UI y escalado
            player = self.objects_manager.get_objects_by_type("player")[0]
            self.hud.render(self.game_window, self.game_surface, player, self.debug_mode)
        
        # Actualizar la pantalla
        pygame.display.update()

    def restart_game(self):
        """Reinicia el estado del juego para una nueva partida."""
        print("Reiniciando juego...")
        try:
            # Limpiar todos los objetos
            self.clear_objects()
            
            # Reiniciar el jugador
            spaceship_img = self.resource_manager.get_image('spaceship')
            damage_img = self.resource_manager.get_image('damage')
            
            level_width = Config.get_level_width()
            player_x = level_width // 2
            player_y = Config.get_level_height() - 50
            player = Player(player_x, player_y)
            player.set_images(spaceship_img, damage_img)
            
            # Registrar el jugador en el motor
            self.register_object(player)

            # Añadir el primer meteorito
            self.meteor_manager.reset()
            self.meteor_manager.create_meteor()

            # Reiniciar contadores
            self.loop_ctr = 0
            self.gameover = False
            print("Juego reiniciado correctamente.")
        except Exception as e:
            print(f"Error al reiniciar juego: {e}")
            import traceback
            traceback.print_exc()

    def cleanup(self):
        """Limpia recursos antes de cerrar."""
        print("Limpiando recursos...")
        # Limpiar recursos del gestor
        self.clear_objects()
        self.resource_manager.clear()
        print("Recursos limpiados correctamente.")
