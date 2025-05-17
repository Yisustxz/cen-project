"""
Clase OtherPlayer - Representa a jugadores remotos controlados por otros clientes.
"""
import pygame
from motor.sprite import GameObject
from space_shooter.data.player_data import PlayerData

class OtherPlayer(GameObject):
    """Clase que representa a otros jugadores en el juego Space Shooter multijugador."""
    
    def __init__(self, x, y, player_id, player_name):
        # La imagen la asignaremos después, cuando esté disponible
        super().__init__(x, y, None, "other_player")
        
        # Identificadores de red
        self.player_id = player_id
        self.player_name = player_name
        
        # Cargar datos de configuración
        player_config = PlayerData.get_player_data()
        
        # Guardar datos del hitbox personalizado
        self.hitbox_data = PlayerData.get_player_hitbox_data()

        # Atributos específicos del jugador desde la configuración
        self.lives = PlayerData.get_player_lives()
        self.score = 0
        
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
        Lógica específica de actualización del jugador remoto.
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
    
    def simulate_damage(self):
        """
        Simula el efecto visual de recibir daño, sin enviar eventos al servidor.
        Usado cuando el servidor notifica que este jugador recibió daño.
        """
        # Calcular frames de invencibilidad desde el damage_time en segundos
        # Asumiendo 60 FPS
        frames_per_second = 60
        invincibility_seconds = PlayerData.get_player_damage_time()
        self.invincibility_frames = int(invincibility_seconds * frames_per_second)
        
        # Comenzar efecto de parpadeo
        self.set_visibility(False)
    
    def on_collide(self, other_entity):
        """
        Maneja la colisión con otra entidad.
        IMPORTANTE: No reacciona a colisiones con meteoritos,
        ya que eso lo maneja el cliente original.
        """
        # No hacer nada, el jugador original maneja sus colisiones
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
        elif event_type == "other_player_hit":
            # Si los datos coinciden con este jugador, mostrar efecto de daño
            if data and 'player_id' in data and data['player_id'] == self.player_id:
                self.simulate_damage()
                if 'lives' in data:
                    self.lives = data['lives']
                return True
        
        return False
        
    def update_position(self, x, y, speed_x, speed_y):
        """
        Actualiza la posición del jugador remoto según datos recibidos del servidor.
        
        Args:
            x: Nueva posición X
            y: Nueva posición Y
            speed_x: Nueva velocidad X
            speed_y: Nueva velocidad Y
        """
        self.x = x
        self.y = y
        self.set_velocity(speed_x, speed_y)
        self.update_hitbox() 