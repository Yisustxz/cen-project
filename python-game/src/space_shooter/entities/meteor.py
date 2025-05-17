"""
Clase Meteor - Representa los meteoritos que caen durante el juego.
"""
import pygame
from motor.sprite import GameObject
from space_shooter.core.constants import GAME_HEIGHT

class Meteor(GameObject):
    """Clase que representa los meteoritos en el juego."""
    
    def __init__(self, image, meteor_type, data, position, speed, rotation):
        """
        Inicializa un nuevo meteorito.
        
        Args:
            image: Imagen del meteorito
            meteor_type: Tipo de meteorito (brown_big, grey_small, etc.)
            data: Diccionario con los datos de configuración
            position: Tupla (x, y) con la posición inicial del meteorito
            speed: Tupla (speed_x, speed_y) con la velocidad en ambos ejes
            rotation: Tupla (angle, speed) con el ángulo inicial y velocidad de rotación
        """
        # Posición proporcionada por el meteor_manager
        x, y = position
        
        # Llamar al constructor de la clase padre con la imagen y tipo
        super().__init__(x, y, image, obj_type="meteor")
        
        # Guardar tipo de meteorito
        self.meteor_type = meteor_type
        
        # Establecer velocidad utilizando el método heredado
        self.set_velocity(speed[0], speed[1])
        
        # Configurar según los datos proporcionados
        self.hp = data.get("hp", 1)
        self.points = data.get("points", 50)
        
        # Configurar rotación proporcionada
        angle, rotation_speed = rotation
        self.set_rotation(angle, rotation_speed)
        
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
        # Ya no es necesario mover el meteorito aquí, lo hace la clase base con el delta time
        
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
            self.set_velocity(0, 0)
            return True
            
        return False
