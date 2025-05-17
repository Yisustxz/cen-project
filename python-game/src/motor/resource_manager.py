"""Gestor de recursos para cargar y gestionar imágenes, sonidos y otros assets."""
import pygame
import os

class ResourceManager:
    """Clase para gestionar y cachear recursos del juego."""
    
    def __init__(self, base_path=None, game=None):
        """
        Inicializa el gestor de recursos.
        
        Args:
            base_path: Ruta base para los recursos (opcional)
            game: Referencia al juego principal (opcional)
        """
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.game = game
        
        # Determinar la ruta base
        if base_path:
            self.base_path = base_path
        else:
            # Si no se proporciona, usar la ruta del proyecto
            self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    def set_game(self, game):
        """
        Establece la referencia al juego principal.
        
        Args:
            game: Referencia al juego principal
        """
        self.game = game
    
    def get_path(self, relative_path):
        """
        Convierte una ruta relativa en una ruta absoluta.
        
        Args:
            relative_path: Ruta relativa desde la ruta base
        
        Returns:
            str: Ruta absoluta
        """
        return os.path.join(self.base_path, relative_path)
    
    def load_image(self, name, path, scale=None, convert_alpha=True):
        """
        Carga una imagen y opcionalmente la escala.
        
        Args:
            name: Nombre para referenciar la imagen
            path: Ruta relativa de la imagen
            scale: Factor de escala o tamaño (opcional)
            convert_alpha: Si se debe usar convert_alpha() para transparencia
        
        Returns:
            Surface: La imagen cargada
        """
        full_path = self.get_path(path)
        
        try:
            image = pygame.image.load(full_path)
            
            # Aplicar convert_alpha para imágenes con transparencia
            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
            
            # Escalar si es necesario
            if scale:
                if isinstance(scale, tuple):
                    # Si scale es una tupla, usarla como tamaño
                    scaled_size = scale
                else:
                    # Si scale es un número, usarlo como factor
                    image_scale = scale / image.get_rect().width
                    new_width = image.get_rect().width * image_scale
                    new_height = image.get_rect().height * image_scale
                    scaled_size = (new_width, new_height)
                
                image = pygame.transform.scale(image, scaled_size)
            
            # Almacenar en caché
            self.images[name] = image
            return image
            
        except pygame.error as e:
            print(f"Error al cargar la imagen {path}: {e}")
            # Crear una superficie de "error" para evitar fallos
            error_surf = pygame.Surface((32, 32))
            error_surf.fill((255, 0, 255))  # Magenta para indicar error
            self.images[name] = error_surf
            return error_surf
    
    def get_image(self, name):
        """
        Obtiene una imagen previamente cargada.
        
        Args:
            name: Nombre de la imagen
        
        Returns:
            Surface: La imagen, o None si no existe
        """
        return self.images.get(name)
    
    def load_sound(self, name, path):
        """
        Carga un sonido.
        
        Args:
            name: Nombre para referenciar el sonido
            path: Ruta relativa del sonido
        
        Returns:
            Sound: El sonido cargado
        """
        full_path = self.get_path(path)
        
        try:
            sound = pygame.mixer.Sound(full_path)
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"Error al cargar el sonido {path}: {e}")
            return None
    
    def get_sound(self, name):
        """
        Obtiene un sonido previamente cargado.
        
        Args:
            name: Nombre del sonido
        
        Returns:
            Sound: El sonido, o None si no existe
        """
        return self.sounds.get(name)
    
    def load_font(self, name, path, size):
        """
        Carga una fuente.
        
        Args:
            name: Nombre para referenciar la fuente
            path: Ruta relativa de la fuente, o None para fuente predeterminada
            size: Tamaño de la fuente
        
        Returns:
            Font: La fuente cargada
        """
        font_key = f"{name}_{size}"
        
        try:
            if path:
                full_path = self.get_path(path)
                font = pygame.font.Font(full_path, size)
            else:
                # Usar fuente predeterminada
                font = pygame.font.Font(pygame.font.get_default_font(), size)
                
            self.fonts[font_key] = font
            return font
        except pygame.error as e:
            print(f"Error al cargar la fuente {path}: {e}")
            # Usar fuente predeterminada en caso de error
            font = pygame.font.Font(pygame.font.get_default_font(), size)
            self.fonts[font_key] = font
            return font
    
    def get_font(self, name, size):
        """
        Obtiene una fuente previamente cargada.
        
        Args:
            name: Nombre de la fuente
            size: Tamaño de la fuente
        
        Returns:
            Font: La fuente, o una fuente predeterminada si no existe
        """
        font_key = f"{name}_{size}"
        
        if font_key in self.fonts:
            return self.fonts[font_key]
        else:
            # Cargar la fuente predeterminada si no existe
            return self.load_font(name, None, size)
    
    def clear(self):
        """Libera todos los recursos cargados."""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear() 