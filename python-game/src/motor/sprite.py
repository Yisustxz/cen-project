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
    
    # Fuente para el modo debug
    debug_font = None
    
    # Constantes para el modo debug
    DEBUG_HITBOX_COLOR = (255, 0, 0)       # Rojo para contorno del hitbox
    DEBUG_CENTER_COLOR = (255, 255, 0)     # Amarillo para centro del hitbox
    DEBUG_SPRITE_CENTER_COLOR = (0, 0, 0)  # Negro para centro del sprite
    DEBUG_CENTER_SIZE = 4                  # Tamaño de los puntos centrales
    
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
        self.has_hitbox = False  # Por defecto NO hay hitbox hasta que se establezca hitbox_data
        self.hitbox = pygame.Rect(0, 0, 0, 0)  # Hitbox vacío inicialmente
        
        # Datos de hitbox (REQUERIDO para tener hitbox)
        self.hitbox_data = None
        
        # Cargar imagen si se proporciona
        if image:
            self.image = image
            self.original_image = image  # Guardar imagen original para rotaciones
        else:
            # Crear un rectángulo por defecto si no hay imagen
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 255, 255))
            self.original_image = self.image
        
        # Inicializar fuente para debug si es necesario
        if GameObject.debug_font is None:
            try:
                # Aumentar el tamaño de la fuente a 14 para mejor legibilidad
                GameObject.debug_font = pygame.font.SysFont("Arial", 14)
            except:
                GameObject.debug_font = pygame.font.Font(None, 14)
    
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
    
    def set_hitbox_data(self, data):
        """
        MÉTODO PRINCIPAL para establecer datos de hitbox.
        Este método DEBE ser llamado para tener un hitbox válido.
        
        Args:
            data: Diccionario con datos de configuración de la hitbox
                Debe contener:
                - width/height: Dimensiones exactas de la hitbox
                Opcional:
                - offset_x/offset_y: Desplazamiento desde el centro
        """
        if not data:
            self.disable_hitbox()
            return
            
        # Guardar los datos
        self.hitbox_data = {
            "width": data.get("width", data.get("hitbox_width", 10)),
            "height": data.get("height", data.get("hitbox_height", 10)),
            "offset_x": data.get("offset_x", 0),
            "offset_y": data.get("offset_y", 0)
        }
        
        # Activar hitbox y aplicar configuración
        self.has_hitbox = True
        self.update_hitbox()
    
    def update_hitbox(self):
        """
        Actualiza el hitbox según la configuración.
        Esta función se llama automáticamente cuando cambia la posición.
        """
        if not self.has_hitbox or not self.hitbox_data:
            return

        # Obtener dimensiones y offsets del hitbox_data
        width = self.hitbox_data.get("width", 10)
        height = self.hitbox_data.get("height", 10)
        offset_x = self.hitbox_data.get("offset_x", 0)
        offset_y = self.hitbox_data.get("offset_y", 0)

        # Crear hitbox con posición basada en offset desde la posición del objeto
        self.hitbox = pygame.Rect(0, 0, width, height)
        
        # Centrar hitbox respecto a la posición del objeto
        self.hitbox.centerx = self.x + offset_x
        self.hitbox.centery = self.y + offset_y
    
    def create_custom_hitbox(self, data):
        """
        Método de compatibilidad - redirige a set_hitbox_data.
        """
        self.set_hitbox_data(data)
    
    def disable_hitbox(self):
        """Desactiva la hitbox del objeto."""
        self.has_hitbox = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.hitbox_data = None
    
    def enable_hitbox(self):
        """Activa la hitbox del objeto si hay datos de hitbox."""
        if self.hitbox_data:
            self.has_hitbox = True
            self.update_hitbox()
    
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
        
        # Actualizar rotación si hay velocidad de rotación
        if self.rotation_speed != 0:
            # Aplicar rotación usando delta time
            self.angle += self.rotation_speed * delta
            self.angle %= 360
            self.update_rotation()
        
        # Actualizar posición de hitbox (EL HITBOX NUNCA ROTA)
        self.update_hitbox()
        
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
        """
        Actualiza la rotación de la imagen, pero NO DEL HITBOX.
        El hitbox se mantiene con su forma y dimensiones originales.
        """
        if self.original_image is not None:
            # Rotar la imagen
            self.image = pygame.transform.rotate(self.original_image, self.angle)

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
            surface.blit(self.image, (self.x, self.y))
    
    def draw_hitbox(self, surface, color=None):
        """
        Dibuja la hitbox como un rectángulo semitransparente con colores específicos según el tipo.
        
        Args:
            surface: Superficie de pygame donde dibujar
            color: Color RGBA para dibujar la hitbox (opcional, se usará un color por defecto según tipo)
        """
        if self.has_hitbox and self.hitbox and self.is_visible:
            # Primero dibujar los puntos centrales y texto usando draw_debug
            self.draw_debug(surface)
            
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
    
    def draw_debug(self, surface):
        """
        Dibuja información de depuración sobre el objeto.
        
        Args:
            surface: Superficie de Pygame donde dibujar
        """
        if self.has_hitbox and self.hitbox and self.is_visible:
            # Dibujar hitbox como rectángulo
            pygame.draw.rect(surface, self.DEBUG_HITBOX_COLOR, self.hitbox, 1)
            
            # Dibujar centro del hitbox como punto amarillo
            center_x = self.hitbox.centerx
            center_y = self.hitbox.centery
            pygame.draw.circle(surface, self.DEBUG_CENTER_COLOR, 
                               (center_x, center_y), self.DEBUG_CENTER_SIZE // 2)
            
            # Dibujar centro del sprite como punto negro
            sprite_center_x = int(self.x)
            sprite_center_y = int(self.y)
            pygame.draw.circle(surface, self.DEBUG_SPRITE_CENTER_COLOR, 
                               (sprite_center_x, sprite_center_y), self.DEBUG_CENTER_SIZE // 2)
            
            # Mostrar información específica para meteoritos
            if self.type == "meteor" and hasattr(self, 'meteor_type'):
                if GameObject.debug_font:
                    # Dibujar tipo de meteorito
                    type_text = GameObject.debug_font.render(self.meteor_type, True, (255, 255, 255))
                    surface.blit(type_text, (self.x, self.y - 20))
                    
                    # Dibujar HP restante si está disponible
                    if hasattr(self, 'hp'):
                        hp_text = GameObject.debug_font.render(f"HP: {self.hp}", True, (255, 255, 255))
                        surface.blit(hp_text, (self.x, self.y - 10))
    
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