"""Implementación del juego Space Shooter."""
import pygame
from pygame.locals import *
import random
import sys

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
from space_shooter.networking.events_manager import NetworkEventsManager
from space_shooter.networking.client import NetworkClient

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
        
        # Inicializar componentes de red si el modo multijugador está habilitado
        self.network_events_manager = None
        self.network_client = None
        
        # Si está habilitado el modo multijugador, inicializar red
        # Sin fallbacks - si la configuración no existe, fallará explícitamente
        multipayer_enabled = Config.get("frontend", "multiplayerMode", "enable")
        if multipayer_enabled:
            print("Modo multijugador activado. Iniciando conexión con el servidor...")
            self.network_events_manager = NetworkEventsManager(self)
            self.network_client = NetworkClient(self.network_events_manager)
            self.network_events_manager.set_client(self.network_client)
            
            # Intentar establecer conexión con el servidor
            if not self.network_client.initialize():
                print("Error al conectar con el servidor. El juego no puede iniciarse en modo multijugador.")
                pygame.quit()
                sys.exit()
        
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
            
            # Si estamos en modo multijugador, asignar el ID del jugador
            if self.network_client and self.network_client.connected:
                player.set_network_ids(self.network_client.player_id)
                # Ya no solicitamos el estado del juego aquí, lo hacemos en el momento de la conexión
                print(f"Jugador configurado con ID de red: {self.network_client.player_id}")
            
            # Registrar el jugador en el motor
            self.register_object(player)

            # Crear el primer meteorito si no estamos en modo multijugador
            multipayer_enabled = Config.get("frontend", "multiplayerMode", "enable")
            if not multipayer_enabled:
                print("Creando meteorito inicial...")
                self.meteor_manager.create_meteor()
                
            # Solicitar estado del juego (jugadores conectados)
            print("Solicitando estado actual del juego...")
            self.execute_request_game_state()

            print("Recursos del juego inicializados correctamente.")
        except Exception as e:
            print(f"Error al inicializar recursos: {e}")
            import traceback
            traceback.print_exc()
            self.quit()

    def execute_request_game_state(self):
        """Solicita el estado actual del juego al servidor."""
        if not self.network_client or not self.network_client.connected:
            return
            
        try:
            # Solicitar estado al servidor
            game_state = self.network_client.request_game_state()
            
            # Logs
            print(f"Estado del juego recibido: {game_state}")
            print(f"Jugadores recibidos: {game_state.players.players}")
            print(f"Meteoros recibidos: {game_state.meteors.meteors}")

            if game_state and game_state.players and hasattr(game_state.players, 'players'):
                # Procesar los jugadores conectados
                for player_data in game_state.players.players:
                    # Ignorar a nuestro propio jugador
                    if player_data.player_id == self.network_client.player_id:
                        continue
                        
                    # Crear evento de conexión para cada jugador existente
                    self.on_online_player_connected({
                        'player_id': player_data.player_id,
                        'player_name': player_data.name,
                        'x': player_data.position.x if player_data.position else 0,
                        'y': player_data.position.y if player_data.position else 0
                    })
                    
                print(f"Estado del juego recibido: {len(game_state.players.players)} jugadores conectados")
            else:
                print("Respuesta de estado de juego vacía o inválida")
                
        except Exception as e:
            print(f"Error al procesar estado del juego: {e}")

    def on_handle_event(self, event):
        """Procesa eventos específicos del juego."""
        if self.gameover and event.type == pygame.KEYDOWN:
            # Verificar si estamos en modo multijugador usando la configuración
            is_multiplayer = Config.get("frontend", "multiplayerMode", "enable")
            
            if event.key == K_y and not is_multiplayer:
                # Solo permitir reiniciar en modo offline
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
        
        # Desconectar del servidor si estamos en modo multijugador
        if self.network_client and self.network_client.connected:
            self.network_client.disconnect()
        
        # Limpiar recursos del gestor
        self.clear_objects()
        self.resource_manager.clear()
        
    # Métodos para manejo de eventos online
    
    def on_online_player_connected(self, data):
        """
        Maneja la conexión de un jugador remoto.
        
        Args:
            data: Datos del jugador conectado
        """
        from space_shooter.entities.other_player import OtherPlayer
        
        if 'player_id' in data and 'x' in data and 'y' in data:
            # Verificar si ya existe este jugador
            remote_players = self.objects_manager.get_objects_by_type("other_player")
            for player in remote_players:
                if player.player_id == data['player_id']:
                    print(f"Jugador {data['player_id']} ya está registrado")
                    return
            
            # Crear objeto OtherPlayer
            player = OtherPlayer(
                data['x'], data['y'], 
                data['player_id'], 
                data.get('player_name', f"Player_{data['player_id']}")
            )
            
            # IMPORTANTE: Asignar imágenes al jugador remoto
            spaceship_img = self.resource_manager.get_image('spaceship')
            damage_img = self.resource_manager.get_image('damage')
            player.set_images(spaceship_img, damage_img)
            
            # Registrar en el motor
            self.register_object(player)
            
            # Notificar UI
            self.emit_event("message", {"text": f"Jugador {data.get('player_name')} se ha unido"})
            print(f"Jugador remoto registrado: ID {data['player_id']}, Nombre {data.get('player_name')}")

    def on_online_player_disconnected(self, data):
        """
        Maneja la desconexión de un jugador remoto.
        
        Args:
            data: Datos del jugador desconectado
        """
        if 'player_id' in data:
            # Buscar el jugador remoto
            remote_players = self.objects_manager.get_objects_by_type("other_player")
            
            for player in remote_players:
                if player.player_id == data['player_id']:
                    # Eliminar del motor
                    self.unregister_object(player)
                    
                    # Notificar UI
                    self.emit_event("message", {
                        "text": f"Jugador {player.player_name} se ha desconectado"
                    })
                    break

    def on_online_player_position(self, data):
        """
        Actualiza la posición de un jugador remoto.
        
        Args:
            data: Datos de posición
        """
        if 'player_id' in data and 'x' in data and 'y' in data:
            # Buscar el jugador remoto
            remote_players = self.objects_manager.get_objects_by_type("other_player")
            
            for player in remote_players:
                if player.player_id == data['player_id']:
                    # Actualizar posición
                    player.update_position(
                        data['x'], data['y'],
                        data.get('speed_x', 0), data.get('speed_y', 0)
                    )
                    break

    def on_online_meteor_created(self, data):
        """
        Crea un meteorito basado en datos del servidor.
        
        Args:
            data: Datos del meteorito con meteor_id, type, x, y, angle, rotation_speed, speed_x, speed_y
        """
        if 'meteor_id' in data and 'type' in data and 'x' in data and 'y' in data:
            print(f"Recibido evento de meteorito creado: ID {data['meteor_id']}, Tipo {data['type']}")
            
            # Preparar datos de velocidad
            speed = (data.get('speed_x', 0), data.get('speed_y', 0))
            
            # Delegar la creación al gestor de meteoritos
            meteor = self.meteor_manager.create_meteor(
                data['type'], 
                (data['x'], data['y']),
                (data.get('angle', 0), data.get('rotation_speed', 0)),
                speed  # Pasar la velocidad
            )
            
            # Asignar ID
            if meteor:
                meteor.set_network_id(data['meteor_id'])
                print(f"Meteorito remoto creado con ID {data['meteor_id']}")
            else:
                print(f"Error: No se pudo crear el meteorito remoto con ID {data['meteor_id']}")
        else:
            print("Error: Datos incompletos para crear meteorito:", data)

    def on_online_missile_fired(self, data):
        """
        Crea un misil basado en los datos del servidor.
        
        Args:
            data: Datos del misil con player_id y missile_id
        """
        if 'player_id' in data:
            from space_shooter.entities.other_missile import OtherMissile
            
            # Encontrar la posición del jugador remoto para crear el misil
            remote_players = self.objects_manager.get_objects_by_type("other_player")
            player_found = False
            
            for player in remote_players:
                if player.player_id == data['player_id']:
                    player_found = True
                    # Crear el misil en la posición del jugador
                    missile_id = data.get('missile_id', 0)
                    
                    # Crear misil justo encima del jugador
                    missile = OtherMissile(
                        player.x, 
                        player.y - player.hitbox.height/2, 
                        missile_id, 
                        player.player_id
                    )
                    
                    # Registrar el misil en el motor
                    self.register_object(missile)
                    print(f"Misil remoto creado para jugador {player.player_id}")
                    break
            
            if not player_found:
                print(f"Advertencia: No se encontró al jugador {data['player_id']} para crear su misil")

    def on_online_meteor_destroyed(self, data):
        """
        Maneja el evento cuando un meteorito es destruido en el servidor.
        
        Args:
            data: Datos del evento con meteor_id y player_id
        """
        if 'meteor_id' in data:
            meteor_id = data['meteor_id']
            player_id = data.get('player_id', 0)
            
            print(f"Recibido evento de meteorito destruido: ID {meteor_id}")
            
            # Buscar el meteorito por su ID
            meteors = self.objects_manager.get_objects_by_type("meteor")
            for meteor in meteors:
                if hasattr(meteor, 'network_id') and meteor.network_id == meteor_id:
                    # Eliminar el meteorito del motor
                    self.unregister_object(meteor)
                    
                    # Si fue destruido por un jugador (player_id > 0), mostrar mensaje
                    if player_id > 0:
                        print(f"Meteorito {meteor_id} destruido por jugador {player_id}")
                    else:
                        print(f"Meteorito {meteor_id} destruido (salió de la pantalla)")
                    
                    return
            
            # Si llegamos aquí, no se encontró el meteorito
            # Esto es normal, ya que el meteorito podría haber sido destruido localmente
            # o aún no haber sido creado en este cliente
            print(f"Meteorito {meteor_id} no encontrado - posiblemente ya destruido localmente")
