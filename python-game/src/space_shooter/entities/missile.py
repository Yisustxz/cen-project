"""
Clase Missile - Representa los misiles disparados por el jugador.
"""
import pygame
from pygame.locals import *
from motor.sprite import GameObject
from space_shooter.core.constants import WHITE, MISSILE_SPEED

class Missile(GameObject):
    """Representa los misiles disparados por el jugador."""

    def __init__(self, x, y):
        # Inicializar primero sin imagen, pero con tipo "missile"
        super().__init__(x, y, obj_type="missile")

        # Crear una superficie personalizada para el misil
        self.image = pygame.Surface((4, 8), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Transparente
        self.original_image = self.image

        # Dibujar el misil como píxeles blancos
        for w in range(self.image.get_width()):
            for h in range(self.image.get_height()):
                self.image.set_at((w, h), WHITE)

        # Configurar rect
        self.rect = self.image.get_rect()
        self.rect.x = x - self.rect.width // 2
        self.rect.y = y

        # Crear una hitbox más grande para facilitar impactos
        # Usar las nuevas funcionalidades de escala
        self.create_hitbox(scale=5.0)  # Hitbox 5 veces más grande que el misil para mayor visibilidad
        
        # Asegurar que la hitbox está centrada con el misil
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery
        
        # Para controlar si debe ser eliminado
        self.should_destroy = False
        self.has_hit = False

    def on_update(self):
        """
        Lógica específica de actualización del misil.
        Este método es llamado automáticamente por la clase base GameObject.
        """
        # El misil sube por la pantalla
        self.y -= MISSILE_SPEED
        
        # Verificar si el misil sigue en pantalla
        if self.rect.bottom <= 0:
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
