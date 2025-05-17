"""Clases base para sprites y objetos del juego."""
import pygame
import math

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
        # Actualizar posición básica
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Actualizar rotación si hay velocidad de rotación
        if self.rotation_speed != 0:
            self.angle += self.rotation_speed
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
            
            # Crear una superficie con canal alpha
            hitbox_surface = pygame.Surface((self.hitbox.width, self.hitbox.height), pygame.SRCALPHA)
            # Llenar con color semitransparente
            hitbox_surface.fill(color)
            # Dibujar en la superficie principal
            surface.blit(hitbox_surface, self.hitbox)
            
            # Dibujar también el borde para mayor visibilidad (usando el mismo color pero sólido)
            border_color = (color[0], color[1], color[2])  # Quitar canal alpha para el borde
            pygame.draw.rect(surface, border_color, self.hitbox, 1)
            
            # Mostrar tamaño de la hitbox
            font = pygame.font.Font(None, 14)  # Fuente pequeña
            size_text = f"{self.hitbox.width}x{self.hitbox.height}"
            text_surf = font.render(size_text, True, (255, 255, 255))
            # Colocar el texto en la esquina superior izquierda de la hitbox
            surface.blit(text_surf, (self.hitbox.left, self.hitbox.top - 15))
    
    def on_game_event(self, event_type, data=None):
        """
        Método para recibir eventos del juego.
        
        Args:
            event_type: Tipo de evento
            data: Datos asociados al evento (opcional)
        
        Returns:
            bool: True si el evento fue manejado, False en caso contrario
        """
        # Por defecto no maneja ningún evento
        return False 