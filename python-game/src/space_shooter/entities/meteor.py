"""
Clase Meteor - Representa los meteoritos que caen durante el juego.
"""
import random
import pygame
from motor.sprite import GameObject
from space_shooter.core.constants import GAME_HEIGHT

class Meteor(GameObject):
    """Clase que representa los meteoritos en el juego."""
    
    def __init__(self, image, meteor_type, data):
        """
        Inicializa un nuevo meteorito.
        
        Args:
            image: Imagen del meteorito
            meteor_type: Tipo de meteorito (brown_big, grey_small, etc.)
            data: Diccionario con los datos de configuración
        """
        # Posición aleatoria en la parte superior de la pantalla
        x = random.randint(0, 800)
        y = -100
        
        # Llamar al constructor de la clase padre con la imagen y tipo
        super().__init__(x, y, image, obj_type="meteor")
        
        # Guardar tipo de meteorito
        self.meteor_type = meteor_type
        
        # Configurar según los datos proporcionados
        speed_x_range = data.get("speed_x_range", (-1, 1))
        speed_y_range = data.get("speed_y_range", (1, 3))
        rotation_range = data.get("rotation_speed_range", (-3, 3))
        
        self.speed_x = random.uniform(speed_x_range[0], speed_x_range[1])
        self.speed_y = random.uniform(speed_y_range[0], speed_y_range[1])
        self.hp = data.get("hp", 1)
        self.points = data.get("points", 50)
        
        # Configurar rotación aleatoria
        rotation_speed = random.uniform(rotation_range[0], rotation_range[1])
        self.set_rotation(random.randint(0, 360), rotation_speed)
        
        # Crear hitbox ajustada
        padding = data.get("hitbox_padding", -5)
        self.create_hitbox(padding=padding)
        
        # Contador para controlar el parpadeo al recibir daño
        self.blink_counter = 0
        
        # Para almacenar puntos ganados al ser destruido
        self.points_earned = 0

    def on_update(self):
        """
        Lógica específica de actualización del meteorito.
        Este método es llamado automáticamente por la clase base GameObject.
        """
        # Mover el meteorito según su velocidad
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Controlar el parpadeo
        if self.blink_counter > 0:
            self.blink_counter -= 1
            if self.blink_counter == 0:
                self.set_visibility(True)
        
        # Verificar si el meteorito debe ser eliminado por estar fuera de pantalla
        if self.y > GAME_HEIGHT or self.x < -100 or self.x > 900:
            if self.game:
                # Notificar al juego que el meteorito sale de la pantalla
                self.game.unregister_object(self)
            self.kill()
    
    def take_damage(self, damage=1):
        """
        Aplica daño al meteorito.
        
        Args:
            damage: Cantidad de daño a aplicar
            
        Returns:
            bool: True si el meteorito fue destruido, False en caso contrario
        """
        self.hp -= damage
        
        # Parpadeo al recibir daño
        self.blink_counter = 10
        self.set_visibility(False)
        
        # Verificar si fue destruido
        if self.hp <= 0:
            self.points_earned = self.points
            
            # Si tiene acceso al juego, notificar la destrucción
            if self.game:
                self.game.emit_event("meteor_destroyed", {
                    "points": self.points,
                    "x": self.x,
                    "y": self.y,
                    "meteor": self
                })
                self.game.unregister_object(self)
                
            self.kill()
            return True
        return False
    
    def on_collide(self, other_entity):
        """Maneja la colisión con otra entidad."""
        if other_entity.type == "missile":
            return self.take_damage()
        return False
    
    def get_points(self):
        """Devuelve los puntos ganados por destruir este meteorito."""
        return self.points_earned

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
            # Detener el movimiento
            self.speed_x = 0
            self.speed_y = 0
            return True
            
        return False
