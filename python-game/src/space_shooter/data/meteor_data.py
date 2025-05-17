"""
Datos y configuración de los meteoritos en el juego.
Este módulo contiene las definiciones de los diferentes tipos de meteoritos
y sus propiedades, incluyendo datos precisos de hitbox.
"""
import random
from entity_config import EntityConfig
from typing import Dict, Union, Tuple, List, Any, Optional
import json
import pygame
import os

CONFIG_PATH = "entities_config.json"

class MeteorData:
    """
    Esta clase proporciona acceso a la configuración de los meteoros
    """
    _instance = None
    _meteor_config = None

    @classmethod
    def get_instance(cls) -> 'MeteorData':
        """Obtiene la instancia singleton de MeteorData"""
        if cls._instance is None:
            cls._instance = MeteorData()
        return cls._instance

    def __init__(self):
        if MeteorData._instance is not None:
            raise Exception("Esta clase es un singleton. Use get_instance() en su lugar.")
        
        try:
            with open(CONFIG_PATH, 'r') as config_file:
                config_data = json.load(config_file)
                self._meteor_config = config_data["meteors"]
        except Exception as e:
            print(f"Error cargando configuración de meteoros: {e}")
            self._meteor_config = {"types": {}, "categories": {}}

    def get_meteor_types(self) -> List[str]:
        """Obtiene la lista de todos los tipos de meteoros disponibles"""
        return list(self._meteor_config["types"].keys())

    def get_meteor_categories(self) -> Dict[str, List[str]]:
        """Obtiene las categorías de meteoros y los tipos que contienen"""
        return self._meteor_config["categories"]

    def get_meteor_types_in_category(self, category: str) -> List[str]:
        """Obtiene los tipos de meteoros en una categoría específica"""
        if category in self._meteor_config["categories"]:
            return self._meteor_config["categories"][category]
        return []

    def get_random_meteor_type(self, category: Optional[str] = None) -> str:
        """
        Obtiene un tipo de meteoro aleatorio.
        Si se especifica una categoría, el tipo se selecciona de esa categoría.
        """
        if category and category in self._meteor_config["categories"]:
            return random.choice(self._meteor_config["categories"][category])
        return random.choice(self.get_meteor_types())

    def get_meteor_config(self, meteor_type: str) -> Dict[str, Any]:
        """Obtiene la configuración completa para un tipo de meteoro específico"""
        if meteor_type in self._meteor_config["types"]:
            return self._meteor_config["types"][meteor_type]
        raise ValueError(f"Tipo de meteoro desconocido: {meteor_type}")

    def get_meteor_image_path(self, meteor_type: str) -> str:
        """Obtiene la ruta de la imagen para un tipo de meteoro específico"""
        config = self.get_meteor_config(meteor_type)
        return f"meteors/{config['image']}"
    
    def get_meteor_hitbox_data(self, meteor_type: str) -> Dict[str, Union[int, float]]:
        """Obtiene los datos del hitbox para un tipo de meteoro específico"""
        config = self.get_meteor_config(meteor_type)
        return {
            "width": config["hitbox_width"],
            "height": config["hitbox_height"],
            "offset_x": config.get("offset_x", 0),
            "offset_y": config.get("offset_y", 0)
        }

    def get_meteor_speed_range(self, meteor_type: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Obtiene el rango de velocidad para un tipo de meteoro específico"""
        config = self.get_meteor_config(meteor_type)
        return (config["speed_x_range"], config["speed_y_range"])
    
    def get_meteor_rotation_speed_range(self, meteor_type: str) -> Tuple[int, int]:
        """Obtiene el rango de velocidad de rotación para un tipo de meteoro específico"""
        config = self.get_meteor_config(meteor_type)
        return config["rotation_speed_range"]
    
    def get_meteor_points(self, meteor_type: str) -> int:
        """Obtiene los puntos otorgados por destruir un meteoro específico"""
        config = self.get_meteor_config(meteor_type)
        return config["points"]
    
    def get_meteor_hp(self, meteor_type: str) -> int:
        """Obtiene los puntos de vida de un tipo de meteoro específico"""
        config = self.get_meteor_config(meteor_type)
        return config["hp"]

    @classmethod
    def get_categories(cls):
        """
        Obtiene las categorías de meteoritos definidas.
        
        Returns:
            dict: Diccionario con las categorías de meteoritos
        """
        return EntityConfig.get_meteor_categories()
    
    @classmethod
    def get_types(cls):
        """
        Obtiene todos los tipos de meteoritos definidos.
        
        Returns:
            list: Lista de tipos de meteoritos
        """
        return EntityConfig.get_meteor_types()

    @classmethod
    def get_random_type(cls, category=None):
        """
        Devuelve un tipo de meteorito aleatorio, opcionalmente dentro de una categoría.
        
        Args:
            category: Categoría específica (big, medium, small, tiny, brown, grey) o None para cualquiera
            
        Returns:
            str: Tipo de meteorito aleatorio
        """
        categories = cls.get_categories()
        
        if category and category in categories:
            return random.choice(categories[category])
        
        # Si no hay categoría o la categoría no existe, elegir de todos los tipos
        types = cls.get_types()
        return random.choice(types)
    
    @classmethod
    def get_type_data(cls, meteor_type=None):
        """
        Obtiene los datos para un tipo específico de meteorito.
        
        Args:
            meteor_type: Tipo de meteorito
            
        Returns:
            dict: Datos del tipo de meteorito
        """
        # Si no se proporciona un tipo, obtener uno aleatorio
        if meteor_type is None:
            meteor_type = cls.get_random_type()
            
        data = EntityConfig.get_meteor_data(meteor_type)
        
        if data:
            return data
        
        # Si el tipo no existe, devolver un tipo aleatorio
        return EntityConfig.get_meteor_data(cls.get_random_type())
    
    @classmethod
    def load_meteor_image(cls, resource_manager, meteor_type):
        """
        Carga y devuelve una imagen para el tipo de meteorito específico.
        
        Args:
            resource_manager: Gestor de recursos para cargar imágenes
            meteor_type: Tipo exacto de meteorito (ej. "brown_big_1")
            
        Returns:
            Surface: Imagen del meteorito
        """
        data = cls.get_type_data(meteor_type)
        image_file = data["image"]
        image_path = f"images/meteors/{image_file}"
        
        # Nombre único para la imagen en el resource manager
        image_name = f"meteor_{meteor_type}"
        
        # Cargar la imagen si no está ya cargada
        if not resource_manager.get_image(image_name):
            resource_manager.load_image(image_name, image_path)
        
        # Devolver la imagen
        return resource_manager.get_image(image_name)
    
    @classmethod
    def get_hitbox_data(cls, meteor_type):
        """
        Obtiene los datos de hitbox para un tipo específico de meteorito.
        
        Args:
            meteor_type: Tipo exacto de meteorito (ej. "brown_big_1")
            
        Returns:
            dict: Datos de hitbox o None si no se encuentra
        """
        data = EntityConfig.get_meteor_data(meteor_type)
        
        if not data:
            return None
            
        return {
            "width": data.get("hitbox_width"),
            "height": data.get("hitbox_height"),
            "offset_x": data.get("offset_x", 0),
            "offset_y": data.get("offset_y", 0),
            "center_x": data.get("center_x"),
            "center_y": data.get("center_y")
        }
