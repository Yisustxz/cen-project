"""
Clase Player - Representa al jugador controlado por el usuario.
"""
import pygame
from motor.sprite import GameObject
from space_shooter.data.player_data import PlayerData
from config import Config

class Player(GameObject):
    """Clase que representa al jugador en el juego Space Shooter."""
    
    def __init__(self, x, y):
        # La imagen la asignaremos después, cuando esté disponible
        super().__init__(x, y, None, "player")
        
        # Cargar datos de configuración
        player_config = PlayerData.get_player_data()
        
        # Guardar datos del hitbox personalizado
        self.hitbox_data = PlayerData.get_player_hitbox_data()
        
        # Asegurarse de que se usen los valores de offset
        self.offset_x = self.hitbox_data.get("offset_x", 0)
        self.offset_y = self.hitbox_data.get("offset_y", 0)
        
        # Atributos específicos del jugador desde la configuración
        self.lives = PlayerData.get_player_lives()
        self.score = 0
        
        # Calcular cooldown en milisegundos desde el delay en segundos
        self.missile_cooldown = int(PlayerData.get_player_fire_delay() * 1000)
        self.last_missile = 0
        
        # Para el sistema de daño e invencibilidad
        self.damage_image = None  # Imagen con efecto de daño
        self.invincibility_frames = 0  # Contador de frames de invencibilidad
        
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
        # Ya no es necesario mover al jugador aquí basado en velocidad, 
        # lo hace la clase base GameObject
        
        # Manejar invencibilidad
        if self.invincibility_frames > 0:
            # Parpadear cada 8 frames
            if self.invincibility_frames % 8 == 0:
                self.toggle_visibility()
            self.invincibility_frames -= 1
        elif not self.is_visible:
            # Asegurar que sea visible cuando termine la invencibilidad
            self.set_visibility(True)
    
    def draw_damage(self, surface):
        """Dibuja el efecto de daño si el jugador ha sido golpeado."""
        # Dibujar daño si está activo
        if self.invincibility_frames > 0 and self.damage_image:
            damage_x = self.x - self.damage_image.get_width() / 3
            damage_y = self.y - self.damage_image.get_height() / 2
            surface.blit(self.damage_image, (damage_x, damage_y))
    
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
        
        # Mover nave a la izquierda
        if keys[K_LEFT] and self.x > 0 - self.offset_x:
            self.set_velocity(-speed, 0)
            action_performed = True
            
        # Mover nave a la derecha
        elif keys[K_RIGHT] and self.x + self.hitbox_data["width"] + self.offset_x < level_width:
            self.set_velocity(speed, 0)
            action_performed = True
            
        # Detener cuando se sueltan las teclas
        else:
            self.set_velocity(0, 0)
            
        # Disparar misil
        if keys[K_SPACE]:
            current_time = pygame.time.get_ticks()
            # Verificar cooldown
            if current_time - self.last_missile > self.missile_cooldown:
                if self.game:
                    # Emitir evento para crear un misil
                    missile_x = self.x + (self.hitbox_data["width"] // 2) + self.offset_x
                    self.game.emit_event("player_fire_missile", {
                        "x": missile_x,
                        "y": self.y
                    })
                    self.last_missile = current_time
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
