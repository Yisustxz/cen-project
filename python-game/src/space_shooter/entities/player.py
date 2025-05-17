"""Representa la nave del jugador."""
import pygame
import math
from motor.sprite import GameObject
from space_shooter.core.constants import PLAYER_LIVES, MISSILE_COOLDOWN

class Player(GameObject):
    def __init__(self, x, y):
        # La imagen la asignaremos después, cuando esté disponible
        super().__init__(x, y, obj_type="player")
        
        self.lives = PLAYER_LIVES
        self.score = 0
        self.damage_image = None
        self.invincibility_frames = 0
        
        # Control de disparo de misiles
        self.missile_cooldown = MISSILE_COOLDOWN
        self.last_missile = pygame.time.get_ticks() - self.missile_cooldown
    
    def set_images(self, image, damage_image):
        """Establece las imágenes para el jugador."""
        self.image = image
        self.original_image = image
        self.damage_image = damage_image
        
        # Actualizar el rect
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Crear una hitbox más pequeña para una colisión más precisa
        # Usar el nuevo método de la clase base
        self.create_hitbox(padding=-10)  # Mayor reducción para mejor visibilidad en modo debug
        
        # Ajustar la posición vertical de la hitbox para el jugador
        self.hitbox.bottom = self.rect.bottom - 2
    
    def on_update(self):
        """
        Lógica específica de actualización del jugador.
        Este método es llamado automáticamente por la clase base GameObject.
        """
        # Ajuste específico para la hitbox del jugador (alineación inferior)
        if self.has_hitbox:
            self.hitbox.centerx = self.rect.centerx
            self.hitbox.bottom = self.rect.bottom - 2
        
        # Efecto de parpadeo durante invencibilidad
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
            damage_x = self.x - self.image.get_width() / 3
            damage_y = self.y - self.image.get_height() / 2
            surface.blit(self.damage_image, (damage_x, damage_y))
    
    def take_damage(self):
        """Aplica daño al jugador si no está en estado de invencibilidad."""
        if self.invincibility_frames == 0:
            # Recibir daño
            self.lives -= 1
            self.invincibility_frames = 50
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
        from space_shooter.core.constants import GAME_WIDTH, PLAYER_SPEED
        
        action_performed = False
        
        # Calcular velocidad actual
        current_speed = PLAYER_SPEED
        
        # Mover nave hacia la izquierda
        if keys[K_LEFT] and self.rect.left > 0:
            self.x -= current_speed
            action_performed = True
            
        # Mover nave hacia la derecha
        elif keys[K_RIGHT] and self.rect.right < GAME_WIDTH:
            self.x += current_speed
            action_performed = True
            
        # Disparar misil
        if keys[K_SPACE]:
            current_time = pygame.time.get_ticks()
            # Verificar cooldown
            if current_time - self.last_missile > self.missile_cooldown:
                if self.game:
                    # Emitir evento para crear un misil
                    self.game.emit_event("player_fire_missile", {
                        "x": self.rect.centerx,
                        "y": self.rect.y
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
