"""
Clase Player - Representa al jugador controlado por el usuario.
"""
import pygame
from pygame.locals import *
from motor.sprite import GameObject
from space_shooter.data.player_data import PlayerData
from space_shooter.entities.missile import Missile
from config import Config

class Player(GameObject):
    """Clase que representa al jugador en el juego Space Shooter."""
    
    def __init__(self, x, y):
        # La imagen la asignaremos después, cuando esté disponible
        super().__init__(x, y, None, "player")
        
        # Identificadores para red - por defecto son None hasta que se conecte al servidor
        self.id = None             # ID único para el objeto (int32)
        self.player_id = None      # ID asignado por el servidor (int32)
        self.player_name = "Player"  # Nombre del jugador por defecto
        
        # Cargar datos de configuración
        player_config = PlayerData.get_player_data()
        
        # Guardar datos del hitbox personalizado
        self.hitbox_data = PlayerData.get_player_hitbox_data()

        # Atributos específicos del jugador desde la configuración
        self.lives = PlayerData.get_player_lives()
        self.score = 0
        
        # Calcular cooldown en milisegundos desde el delay en segundos
        self.missile_cooldown = int(PlayerData.get_player_fire_delay() * 1000)
        self.last_missile = 0
        
        # Para el sistema de daño e invencibilidad
        self.damage_image = None  # Imagen con efecto de daño
        self.invincibility_frames = 0  # Contador de frames de invencibilidad
        
        # Para mostrar el nombre del jugador
        self.name_font = pygame.font.Font(None, 20)  # Fuente pequeña
        self.render_name()
        
        # Para controlar el evento STOP
        self.at_border = False
        
    def render_name(self):
        """Renderiza el nombre del jugador como una superficie."""
        if self.player_name:
            # Color azul para el jugador local
            blue_color = (0, 120, 255)  # Azul claro
            self.name_surface = self.name_font.render(self.player_name, True, blue_color)
        else:
            self.name_surface = None
        
    def set_network_ids(self, player_id, object_id=None):
        """
        Establece los identificadores de red para este jugador.
        
        Args:
            player_id: ID asignado por el servidor para este jugador (int32)
            object_id: ID único del objeto (opcional, se usará player_id si no se proporciona)
        """
        self.player_id = player_id
        self.id = object_id if object_id is not None else player_id
    
    def set_images(self, image, damage_image):
        """
        Establece las imágenes del jugador.
        
        Args:
            image: Imagen principal de la nave
            damage_image: Imagen con efecto de daño
        """
        self.image = image
        self.original_image = image
        self.damage_image = damage_image
        
        # Aplicar hitbox
        self.set_hitbox_data(self.hitbox_data)
    
    def on_update(self):
        """
        Lógica específica de actualización del jugador.
        Este método es llamado automáticamente por la clase base GameObject.
        """
        # Manejar invencibilidad
        if self.invincibility_frames > 0:
            # Parpadear cada 8 frames
            if self.invincibility_frames % 8 == 0:
                self.toggle_visibility()
            self.invincibility_frames -= 1
        elif not self.is_visible:
            # Asegurar que sea visible cuando termine la invencibilidad
            self.set_visibility(True)
        
        # Notificar cambio de posición al servidor si está en modo multijugador
        if self.player_id is not None:
            game = self.get_game()
            if game and game.network_events_manager:
                game.network_events_manager.on_player_position_changed(self)
    
    def draw(self, surface):
        """
        Dibuja el jugador en la superficie dada.
        Sobrescribe el método draw de GameObject para añadir el nombre.
        
        Args:
            surface: Superficie donde dibujar
        """
        # Llamar al método de dibujo de la clase base
        super().draw(surface)
        
        # Dibujar el nombre sobre el jugador
        if self.is_visible and self.name_surface:
            # Calcular posición del nombre (centrado sobre el jugador)
            name_rect = self.name_surface.get_rect()
            name_rect.centerx = self.x
            name_rect.bottom = self.y - self.image.get_height() // 2 - 5  # 5 píxeles arriba de la nave
            
            # Crear un fondo negro semitransparente
            bg_rect = name_rect.copy()
            bg_rect.inflate_ip(4, 4)  # Hacer el fondo un poco más grande
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))  # Negro semitransparente
            
            # Dibujar el fondo y luego el texto
            surface.blit(bg_surface, bg_rect)
            surface.blit(self.name_surface, name_rect)
    
    def draw_damage(self, surface):
        """Dibuja el efecto de daño si el jugador ha sido golpeado."""
        # Dibujar daño si está activo
        if self.invincibility_frames > 0 and self.damage_image:
            # Obtener offsets del hitbox_data
            offset_x = self.hitbox_data.get("offset_x", 0) if self.hitbox_data else 0
            offset_y = self.hitbox_data.get("offset_y", 0) if self.hitbox_data else 0
            
            # Calcular posición ajustando offsets para que el sprite se coloque correctamente
            rect = self.damage_image.get_rect()
            rect.centerx = self.x - offset_x
            rect.centery = self.y - offset_y
            
            surface.blit(self.damage_image, rect)
    
    def take_damage(self):
        """Aplica daño al jugador si no está en estado de invencibilidad."""
        if self.invincibility_frames == 0:
            # Recibir daño
            self.lives -= 1
            
            # Calcular frames de invencibilidad desde el damage_time en segundos
            # Asumiendo 60 FPS
            frames_per_second = 60
            invincibility_seconds = PlayerData.get_player_damage_time()
            self.invincibility_frames = int(invincibility_seconds * frames_per_second)
            
            # Comenzar efecto de parpadeo
            self.set_visibility(False)
            return True
        return False
    
    def add_score(self, points):
        """Añade puntos al marcador del jugador."""
        self.score += points
        
    def on_collide(self, other_entity):
        """Maneja la colisión con otra entidad."""
        if other_entity.type == "meteor" and self.invincibility_frames == 0:
            self.take_damage()
            return True
        return False

    def on_game_event(self, event_type, data=None):
        """
        Maneja eventos emitidos por el juego.
        
        Args:
            event_type: Tipo de evento
            data: Datos asociados al evento (opcional)
            
        Returns:
            bool: True si el evento fue manejado, False en caso contrario
        """
        if event_type == "game_over":
            # Mostrar animación de game over
            self.set_visibility(True)  # Asegurar que sea visible en game over
            # Detener movimiento
            self.set_velocity(0, 0)
            return True
        elif event_type == "meteor_destroyed":
            # Reaccionar a la destrucción de un meteorito
            # Por ejemplo, mostrar una animación especial si el meteorito
            # fue destruido cerca del jugador
            if data and 'x' in data and 'y' in data:
                distance = ((self.x - data['x'])**2 + (self.y - data['y'])**2)**0.5
                if distance < 100:  # Si el meteorito explotó cerca
                    # Aquí podríamos activar algún efecto especial
                    pass
            return True
        
        return False
    
    def handle_input(self, keys):
        """
        Maneja las entradas de teclado para el movimiento y disparo.
        
        Args:
            keys: Estado actual de las teclas
            
        Returns:
            bool: True si se realizó alguna acción, False en caso contrario
        """
        from pygame.locals import K_LEFT, K_RIGHT, K_SPACE
        
        action_performed = False
        
        # Obtener velocidad desde la configuración
        speed = PlayerData.get_player_speed()
        
        # Obtener el ancho del nivel para limitar el movimiento
        level_width = Config.get_level_width()
        
        # Caso especial: detectar colisión con los bordes
        at_border_now = False
        
        # Mover nave a la izquierda - Verificar que el hitbox no salga del límite izquierdo
        if keys[K_LEFT] and self.hitbox.left > 0:
            self.set_velocity(-speed, 0)
            action_performed = True
        elif keys[K_LEFT] and self.hitbox.left <= 0:
            # Detener en el borde izquierdo
            self.set_velocity(0, 0)
            at_border_now = True
            
        # Mover nave a la derecha - Verificar que el hitbox no salga del límite derecho
        elif keys[K_RIGHT] and self.hitbox.right < level_width:
            self.set_velocity(speed, 0)
            action_performed = True
        elif keys[K_RIGHT] and self.hitbox.right >= level_width:
            # Detener en el borde derecho
            self.set_velocity(0, 0)
            at_border_now = True
            
        # Detener cuando se sueltan las teclas
        else:
            self.set_velocity(0, 0)
            
        # Verificar si ha cambiado el estado de colisión con el borde
        if at_border_now != self.at_border:
            self.at_border = at_border_now
            
            # Si está en modo multijugador, notificar al servidor que el jugador se detuvo en el borde
            if at_border_now and self.player_id is not None:
                game = self.get_game()
                if game and hasattr(game, 'network_events_manager') and game.network_events_manager:
                    # Forzar actualización de posición con velocidad 0
                    self.speed_x = 0
                    self.speed_y = 0
                    game.network_events_manager.on_player_position_changed(self, force_stop=True)
        
        # Disparar misil
        if keys[K_SPACE]:
            # Usar el nuevo método fire_missile
            missile = self.fire_missile()
            if missile and self.game:
                # Registrar el misil con el juego
                self.game.register_object(missile)
            action_performed = True
        
        return action_performed
        
    def add_lives(self, lives):
        """
        Añade vidas al jugador.
        
        Args:
            lives: Número de vidas a añadir
        """
        self.lives += lives
        print(f"Jugador obtuvo {lives} vida(s) extra")
        
    def fire_missile(self):
        """
        Crea un nuevo misil en la posición del jugador.
        El misil es creado en el centro superior del jugador.
        """
        # Comprobar si el tiempo transcurrido es suficiente para disparar
        current_time = pygame.time.get_ticks()
        if current_time - self.last_missile < self.missile_cooldown:
            return None  # No ha pasado suficiente tiempo
            
        # Actualizar tiempo del último disparo
        self.last_missile = current_time
        
        # Crear un nuevo misil en la posición del jugador
        # Usamos self.x y self.y que ahora son el centro del hitbox
        # El misil se sitúa en el centro superior
        missile = Missile(self.x, self.y - self.hitbox.height/2, self.player_id)
        
        # Si tiene acceso al juego, notificar que se creó un misil
        if self.game:
            self.game.emit_event("missile_fired", {
                "player_id": self.player_id,
                "x": self.x, 
                "y": self.y - self.hitbox.height/2
            })
            
            # Notificar al servidor en modo multijugador
            if self.player_id is not None and hasattr(self.game, 'network_events_manager') and self.game.network_events_manager:
                self.game.network_events_manager.on_player_fired_missile({
                    "x": self.x, 
                    "y": self.y - self.hitbox.height/2,
                    "player_id": self.player_id
                })
        
        return missile
