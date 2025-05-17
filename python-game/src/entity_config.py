"""
Módulo de configuración para entidades del juego.
Carga datos de configuración para las entidades desde un archivo JSON.
"""
import os
import json
import sys
import logging

# Configurar logging
logger = logging.getLogger("entity_config")

# Archivo de configuración de entidades
CONFIG_FILE = "entities_config.json"

# Caché para la configuración
_config_cache = None

def get_base_path():
    """
    Obtiene la ruta base del proyecto.
    
    Returns:
        str: Ruta base del proyecto
    """
    # Obtener la ruta del directorio donde está este script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Ir dos niveles arriba para llegar a la raíz del proyecto
    return os.path.abspath(os.path.join(current_dir, '..', '..'))

def load_entities_config():
    """
    Carga la configuración de entidades desde el archivo JSON.
    
    Returns:
        dict: Configuración de entidades
    """
    global _config_cache
    
    # Si ya está en caché, devolverla
    if _config_cache is not None:
        return _config_cache
    
    try:
        # Construir la ruta completa al archivo de configuración
        config_path = os.path.join(get_base_path(), CONFIG_FILE)
        
        # Verificar si el archivo existe
        if not os.path.exists(config_path):
            logger.error(f"Archivo de configuración de entidades no encontrado: {config_path}")
            _config_cache = {}
            return _config_cache
            
        # Cargar el archivo de configuración
        with open(config_path, 'r') as config_file:
            _config_cache = json.load(config_file)
            logger.info("Configuración de entidades cargada exitosamente")
            return _config_cache
            
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar el archivo JSON de entidades: {str(e)}")
        _config_cache = {}
        return _config_cache
        
    except Exception as e:
        logger.error(f"Error al cargar la configuración de entidades: {str(e)}")
        _config_cache = {}
        return _config_cache

class EntityConfig:
    """
    Clase para acceder a la configuración de entidades del juego.
    """
    
    @classmethod
    def get_meteor_types(cls):
        """
        Obtiene todos los tipos de meteoritos definidos.
        
        Returns:
            list: Lista de tipos de meteoritos
        """
        config = load_entities_config()
        if "meteors" in config and "types" in config["meteors"]:
            # Obtener todas las claves del diccionario de tipos
            meteor_types = list(config["meteors"]["types"].keys())
            return meteor_types
        return []
    
    @classmethod
    def get_meteor_categories(cls):
        """
        Obtiene las categorías de meteoritos definidas.
        
        Returns:
            dict: Diccionario con las categorías de meteoritos
        """
        config = load_entities_config()
        if "meteors" in config and "categories" in config["meteors"]:
            return config["meteors"]["categories"]
        return {}
    
    @classmethod
    def get_meteor_data(cls, meteor_type):
        """
        Obtiene los datos para un tipo de meteorito específico.
        
        Args:
            meteor_type: Tipo de meteorito
            
        Returns:
            dict: Datos del meteorito o diccionario vacío si no existe
        """
        config = load_entities_config()
        if "meteors" in config and "types" in config["meteors"] and meteor_type in config["meteors"]["types"]:
            return config["meteors"]["types"][meteor_type]
        return {}
    
    @classmethod
    def get_player_data(cls):
        """
        Obtiene los datos de configuración del jugador.
        
        Returns:
            dict: Datos del jugador o diccionario vacío si no existe
        """
        config = load_entities_config()
        if "player" in config:
            return config["player"]
        return {}
    
    @classmethod
    def get_missile_data(cls):
        """
        Obtiene los datos de configuración de los misiles.
        
        Returns:
            dict: Datos de los misiles o diccionario vacío si no existe
        """
        config = load_entities_config()
        if "missile" in config:
            return config["missile"]
        return {}

# Cargar la configuración al importar el módulo
load_entities_config() 