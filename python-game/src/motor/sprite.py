"""Clases base para sprites y objetos del juego."""
import pygame
import math
import sys
import os

# Añadir el directorio src al path para poder importar
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la utilidad de delta time
from space_shooter.utils.delta_time import DeltaTime

class GameObject(pygame.sprite.Sprite):
    """Clase base para todos los objetos del juego con hitbox personalizada."""
    
    def __init__(self, x, y, image=None, obj_type=None):
        """
        Inicializa un objeto del juego.
        
        Args:
            x: Posición X inicial
            y: Posición Y inicial
            image: Imagen del objeto (opcional)
            obj_type: Tipo de objeto (opcional)
        """
        pygame.sprite.Sprite.__init__(self)
        
        self.x = x
        self.y = y
        
        # Vectores de velocidad para movimiento independiente de FPS
        self.speed_x = 0
        self.speed_y = 0
        
        # Tipo de objeto (para clasificación y manejo)
        self.type = obj_type or self.__class__.__name__
        
        # Referencia al juego principal (opcional)
        self.game = None
        
        # Estado de visibilidad
        self.is_visible = True
        
        # Ángulo de rotación y velocidad de rotación
        self.angle = 0
        self.rotation_speed = 0
        
        # Control de hitbox
        self.has_hitbox = True  # Indica si el objeto tiene hitbox
        self.hitbox_scale = 1.0  # Factor de escala para la hitbox (1.0 = tamaño completo)
        self.hitbox_padding = 0  # Padding negativo (reducción) o positivo (expansión) en pixels
        
        # Cargar imagen si se proporciona
        if image:
            self.image = image
            self.original_image = image  # Guardar imagen original para rotaciones
        else:
            # Crear un rectángulo por defecto si no hay imagen
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 255, 255))
            self.original_image = self.image
        
        # Crear rect
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Crear hitbox predeterminada con el mismo tamaño que el rect
        self.create_hitbox()
    
    def set_game(self, game):
        """
        Establece la referencia al juego principal.
        
        Args:
            game: Referencia al juego principal
        """
        self.game = game
    
    def get_game(self):
        """
        Devuelve la referencia al juego principal.
        
        Returns:
            object: Referencia al juego principal
        """
        return self.game
    
    def set_type(self, obj_type):
        """
        Establece el tipo de objeto.
        
        Args:
            obj_type: Tipo de objeto
        """
        self.type = obj_type
    
    def set_rotation(self, angle, speed=0):
        """
        Establece el ángulo y velocidad de rotación.
        
        Args:
            angle: Ángulo inicial en grados
            speed: Velocidad de rotación en grados por frame
        """
        self.angle = angle
        self.rotation_speed = speed
    
    def set_velocity(self, speed_x, speed_y):
        """
        Establece la velocidad del objeto en ambos ejes.
        
        Args:
            speed_x: Velocidad en el eje X (pixels por segundo)
            speed_y: Velocidad en el eje Y (pixels por segundo)
        """
        self.speed_x = speed_x
        self.speed_y = speed_y
    
    def get_velocity(self):
        """
        Obtiene la velocidad actual del objeto.
        
        Returns:
            tuple: (speed_x, speed_y) Velocidad en ambos ejes
        """
        return (self.speed_x, self.speed_y)
    
    def create_hitbox(self, scale=None, padding=None):
        """
        Crea o actualiza la hitbox basada en la imagen actual.
        
        Args:
            scale: Factor de escala (1.0 = tamaño completo)
            padding: Padding negativo (reducción) o positivo (expansión) en pixels
        """
        if scale is not None:
            self.hitbox_scale = scale
        if padding is not None:
            self.hitbox_padding = padding
            
        if not self.has_hitbox:
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            return
            
        # Calcular dimensiones de la hitbox
        if self.hitbox_scale != 1.0:
            # Escalar basado en porcentaje
            width = int(self.rect.width * self.hitbox_scale)
            height = int(self.rect.height * self.hitbox_scale)
        else:
            # Usar padding en pixels
            width = self.rect.width + (self.hitbox_padding * 2)
            height = self.rect.height + (self.hitbox_padding * 2)
            
        # Asegurar dimensiones mínimas
        width = max(width, 1)
        height = max(height, 1)
        
        # Crear la hitbox
        self.hitbox = pygame.Rect(0, 0, width, height)
        self.update_hitbox_position()
    
    def disable_hitbox(self):
        """Desactiva la hitbox del objeto."""
        self.has_hitbox = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)
    
    def enable_hitbox(self):
        """Activa la hitbox del objeto."""
        self.has_hitbox = True
        self.create_hitbox()
    
    def update_hitbox_position(self):
        """Actualiza la posición de la hitbox para que coincida con el rect."""
        if self.has_hitbox:
            self.hitbox.center = self.rect.center
    
    def update(self):
        """
        Método principal de actualización llamado por el motor de juego.
        Sigue el patrón Hollywood: actualiza primero lo común y luego llama al 
        método específico de la clase derivada.
        """
        # Aplicar velocidad usando delta time para movimiento independiente de FPS
        delta = DeltaTime.get_delta()
        if self.speed_x != 0:
            self.x += self.speed_x * delta
        if self.speed_y != 0:
            self.y += self.speed_y * delta
        
        # Actualizar posición básica
        self.rect.x = int(self.x)  # Convertir a entero para evitar problemas de precisión
        self.rect.y = int(self.y)
        
        # Actualizar rotación si hay velocidad de rotación
        if self.rotation_speed != 0:
            # Aplicar rotación usando delta time
            self.angle += self.rotation_speed * delta
            self.angle %= 360
            self.update_rotation()
        
        # Actualizar posición de hitbox
        self.update_hitbox_position()
        
        # Llamar al método específico de la clase derivada
        # Esto permite que cada objeto implemente su lógica específica
        self.on_update()
    
    def on_update(self):
        """
        Método que deben sobrescribir las clases derivadas para
        implementar su lógica específica de actualización.
        """
        pass  # Por defecto no hace nada
    
    def update_rotation(self):
        """Actualiza la rotación de la imagen y ajusta el rect y hitbox."""
        if self.original_image is not None:
            # Rotar la imagen
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            
            # Actualizar el rect manteniendo el centro
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            
            # Si la hitbox está habilitada, actualizarla para la rotación
            if self.has_hitbox:
                # Recalcular la hitbox para la imagen rotada
                self.create_hitbox()
                self.hitbox.center = self.rect.center
    
    def set_visibility(self, visible):
        """
        Establece si el objeto es visible o no.
        
        Args:
            visible: True para hacer visible, False para invisible
        """
        self.is_visible = visible
    
    def toggle_visibility(self):
        """Alterna el estado de visibilidad del objeto."""
        self.is_visible = not self.is_visible
    
    def collides_with(self, other):
        """
        Comprueba si este objeto colisiona con otro usando hitboxes.
        
        Args:
            other: Otro objeto GameObject
            
        Returns:
            bool: True si hay colisión, False en caso contrario
        """
        if not (self.has_hitbox and hasattr(other, 'has_hitbox') and other.has_hitbox):
            return False
        return self.hitbox.colliderect(other.hitbox)
    
    def draw(self, surface):
        """
        Dibuja el objeto en la superficie proporcionada.
        
        Args:
            surface: Superficie de pygame donde dibujar
        """
        if self.is_visible:
            surface.blit(self.image, self.rect)
    
    def draw_hitbox(self, surface, color=None):
        """
        Dibuja la hitbox como un rectángulo semitransparente con colores específicos según el tipo.
        
        Args:
            surface: Superficie de pygame donde dibujar
            color: Color RGBA para dibujar la hitbox (opcional, se usará un color por defecto según tipo)
        """
        if self.has_hitbox and self.is_visible:
            # Definir colores por tipo de objeto si no se especifica un color
            if color is None:
                if self.type == "player":
                    color = (0, 255, 0, 128)  # Verde para el jugador
                elif self.type == "meteor":
                    color = (255, 0, 0, 128)  # Rojo para meteoritos
                elif self.type == "missile":
                    color = (0, 0, 255, 128)  # Azul para misiles
                else:
                    color = (255, 255, 0, 128)  # Amarillo para otros objetos
            
            # Crear una superficie semitransparente
            hitbox_surface = pygame.Surface((self.hitbox.width, self.hitbox.height), pygame.SRCALPHA)
            hitbox_surface.fill(color)
            
            # Dibujar en la superficie del juego
            surface.blit(hitbox_surface, self.hitbox)
    
    def emit_event(self, event_type, data=None):
        """
        Emite un evento al juego si tiene referencia al mismo.
        
        Args:
            event_type: Tipo de evento
            data: Datos asociados al evento (opcional)
            
        Returns:
            bool: True si se pudo emitir el evento, False en caso contrario
        """
        if self.game and hasattr(self.game, 'emit_event'):
            self.game.emit_event(event_type, data)
            return True
        return False
    
    def play_sound(self, sound_name):
        """
        Reproduce un sonido usando el gestor de recursos del juego.
        
        Args:
            sound_name: Nombre del sonido
            
        Returns:
            bool: True si se pudo reproducir el sonido, False en caso contrario
        """
        if self.game and hasattr(self.game, 'resource_manager'):
            if self.game.resource_manager.play_sound(sound_name):
                return True
        return False
    
    def on_game_event(self, event_type, data=None):
        """
        Maneja eventos emitidos por el juego.
        Este método debe ser sobrescrito por clases derivadas para
        implementar el manejo específico de eventos.
        
        Args:
            event_type: Tipo de evento
            data: Datos asociados al evento (opcional)
            
        Returns:
            bool: True si el evento fue manejado, False en caso contrario
        """
        return False  # Por defecto no maneja ningún evento 