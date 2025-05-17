"""
Clase Missile - Representa los proyectiles disparados por el jugador.
"""
import pygame
from motor.sprite import GameObject
from space_shooter.data.player_data import PlayerData
from space_shooter.core.constants import WHITE

class Missile(GameObject):
    """Clase que representa los misiles disparados por el jugador."""
    
    def __init__(self, x, y):
        # Inicializar primero sin imagen, pero con tipo "missile"
        super().__init__(x, y, None, obj_type="missile")
        
        # Cargar datos de configuración
        missile_config = PlayerData.get_missile_data()
        
        # Ajustar el hitbox para hacerlo más pequeño
        self.hitbox_data = PlayerData.get_missile_hitbox_data()
        
        # Obtener velocidad desde la configuración
        missile_speed = PlayerData.get_missile_speed()
        
        # Guardar el daño que causa este misil
        self.damage = PlayerData.get_missile_damage()
        
        # Crear una simple imagen blanca para el misil
        # Usamos las dimensiones del hitbox para la imagen
        width = self.hitbox_data["width"] // 2  # Hacer la imagen más pequeña que el hitbox
        height = self.hitbox_data["height"] // 2
        
        self.image = pygame.Surface((width, height))
        self.original_image = self.image

        # Dibujar el misil como píxeles blancos
        for w in range(self.image.get_width()):
            for h in range(self.image.get_height()):
                self.image.set_at((w, h), WHITE)

        # Ajustar posición para centrar el misil en X
        self.x = x - (width // 2)
        
        # Establecer velocidad usando los datos de configuración
        self.set_velocity(0, -missile_speed)


        # Aplicar hitbox con los datos de configuración ajustados
        self.set_hitbox_data(self.hitbox_data)
        
        # Para controlar si debe ser eliminado
        self.should_destroy = False
        self.has_hit = False

    def on_update(self):
        """
        Lógica específica de actualización del misil.
        Este método es llamado automáticamente por la clase base GameObject.
        """
        # Ya no es necesario mover el misil, lo hace la clase base con delta time
        
        # Verificar si el misil sigue en pantalla
        if self.hitbox.bottom <= 0:
            self.should_destroy = True
            
        # Si debe ser destruido, notificar al juego y eliminarse
        if self.should_destroy and self.game:
            # Notificar al juego que debe ser eliminado
            self.game.emit_event("missile_destroyed", {"missile": self})
            
            # Eliminar el misil del registro
            self.game.unregister_object(self)
            self.kill()  # Eliminar de todos los grupos de sprites
    
    def on_collide(self, other_entity):
        """Maneja la colisión con otra entidad."""
        if other_entity.type == "meteor" and not self.has_hit:
            self.has_hit = True
            self.should_destroy = True
            return True
        return False
    
    def get_damage(self):
        """
        Obtiene el daño que causa este misil.
        
        Returns:
            int: Cantidad de daño que inflige el misil
        """
        return self.damage
    
    def should_be_destroyed(self):
        """
        Comprueba si el misil debe ser eliminado.
        
        Returns:
            bool: True si el misil debe ser eliminado, False en caso contrario
        """
        return self.should_destroy

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
            # Auto-destruir el misil cuando termina el juego
            self.should_destroy = True
            return True
        elif event_type == "meteor_destroyed":
            # Si un meteorito fue destruido cerca, el misil podría reaccionar
            if data and 'x' in data and 'y' in data:
                distance = ((self.x - data['x'])**2 + (self.y - data['y'])**2)**0.5
                if distance < 50:  # Si el meteorito explotó muy cerca
                    # Crear efecto visual, si el misil tiene acceso al juego
                    # se podría crear un efecto particular aquí
                    self.should_destroy = True
                    return True
        
        return False
