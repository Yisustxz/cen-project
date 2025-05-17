"""
Datos y configuración de los meteoritos en el juego.
Este módulo contiene las definiciones de los diferentes tipos de meteoritos
y sus propiedades.
"""
import random

class MeteorData:
    """Clase que contiene los datos de los meteoritos."""
    
    # Tipos de meteoritos disponibles
    TYPES = {
        "brown_big": {
            "speed_x_range": (-1, 1),
            "speed_y_range": (1, 3),
            "hp": 3,
            "points": 100,
            "rotation_speed_range": (-3, 3),
            "hitbox_padding": -10,
            "images": ["brown_big_1.png", "brown_big_2.png"]
        },
        "brown_medium": {
            "speed_x_range": (-1.5, 1.5),
            "speed_y_range": (2, 4),
            "hp": 2,
            "points": 75,
            "rotation_speed_range": (-3, 3),
            "hitbox_padding": -8,
            "images": ["brown_medium_1.png", "brown_medium_2.png"]
        },
        "brown_small": {
            "speed_x_range": (-2, 2),
            "speed_y_range": (2, 5),
            "hp": 1,
            "points": 50,
            "rotation_speed_range": (-4, 4),
            "hitbox_padding": -5,
            "images": ["brown_small_1.png", "brown_small_2.png"]
        },
        "brown_tiny": {
            "speed_x_range": (-2.5, 2.5),
            "speed_y_range": (3, 6),
            "hp": 1,
            "points": 25,
            "rotation_speed_range": (-5, 5),
            "hitbox_padding": -3,
            "images": ["brown_tiny_1.png", "brown_tiny_2.png"]
        },
        "grey_big": {
            "speed_x_range": (-0.8, 0.8),
            "speed_y_range": (1, 2.5),
            "hp": 4,
            "points": 120,
            "rotation_speed_range": (-2, 2),
            "hitbox_padding": -12,
            "images": ["grey_big_1.png", "grey_big_2.png"]
        },
        "grey_medium": {
            "speed_x_range": (-1.2, 1.2),
            "speed_y_range": (1.5, 3.5),
            "hp": 2,
            "points": 80,
            "rotation_speed_range": (-3, 3),
            "hitbox_padding": -8,
            "images": ["grey_medium_1.png", "grey_medium_2.png"]
        },
        "grey_small": {
            "speed_x_range": (-1.8, 1.8),
            "speed_y_range": (2, 4.5),
            "hp": 1,
            "points": 60,
            "rotation_speed_range": (-4, 4),
            "hitbox_padding": -5,
            "images": ["grey_small_1.png", "grey_small_2.png"]
        },
        "grey_tiny": {
            "speed_x_range": (-2.2, 2.2),
            "speed_y_range": (2.5, 5.5),
            "hp": 1,
            "points": 30,
            "rotation_speed_range": (-5, 5),
            "hitbox_padding": -3,
            "images": ["grey_tiny_1.png", "grey_tiny_2.png"]
        }
    }
    
    @classmethod
    def get_random_type(cls):
        """
        Devuelve un tipo de meteorito aleatorio.
        
        Returns:
            str: Tipo de meteorito aleatorio
        """
        return random.choice(list(cls.TYPES.keys()))
    
    @classmethod
    def get_type_data(cls, meteor_type):
        """
        Obtiene los datos para un tipo específico de meteorito.
        
        Args:
            meteor_type: Tipo de meteorito
            
        Returns:
            dict: Datos del tipo de meteorito
        """
        if meteor_type in cls.TYPES:
            return cls.TYPES[meteor_type]
        
        # Si el tipo no existe, devolver un tipo aleatorio
        return cls.TYPES[cls.get_random_type()]
    
    @classmethod
    def get_random_data(cls):
        """
        Obtiene datos para un tipo aleatorio de meteorito.
        
        Returns:
            tuple: (tipo, datos)
        """
        meteor_type = cls.get_random_type()
        return meteor_type, cls.TYPES[meteor_type]
    
    @classmethod
    def load_meteor_image(cls, resource_manager, meteor_type):
        """
        Carga y devuelve una imagen aleatoria para el tipo de meteorito.
        
        Args:
            resource_manager: Gestor de recursos para cargar imágenes
            meteor_type: Tipo de meteorito
            
        Returns:
            Surface: Imagen del meteorito
        """
        data = cls.get_type_data(meteor_type)
        image_file = random.choice(data["images"])
        image_path = f"images/meteors/{image_file}"
        
        # Nombre único para la imagen en el resource manager
        image_name = f"meteor_{meteor_type}_{image_file}"
        
        # Cargar la imagen si no está ya cargada
        if not resource_manager.get_image(image_name):
            resource_manager.load_image(image_name, image_path)
        
        return resource_manager.get_image(image_name) 