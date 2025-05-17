"""
Módulo de configuración para el juego Space Shooter.
Implementa un patrón Singleton para acceder a la configuración desde cualquier parte de la aplicación.
"""
import json
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("config")

# Ruta al archivo de configuración
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'))

class Config:
    """
    Clase para gestionar la configuración del juego.
    Permite acceder a la configuración desde cualquier parte de la aplicación mediante métodos estáticos.
    """
    
    # Configuración cargada
    _config = None
    
    @classmethod
    def load_config(cls):
        """
        Carga la configuración desde el archivo config.json.
        
        Returns:
            dict: Configuración cargada o configuración por defecto si hay error.
        """
        try:
            # Verificar si el archivo existe
            if not os.path.exists(CONFIG_PATH):
                logger.warning(f"Archivo de configuración no encontrado: {CONFIG_PATH}")
                cls._config = cls._create_default_config()
                return cls._config
                
            # Cargar el archivo de configuración
            with open(CONFIG_PATH, 'r') as config_file:
                cls._config = json.load(config_file)
                logger.info("Configuración cargada exitosamente")
                return cls._config
                
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar el archivo JSON: {str(e)}")
            cls._config = cls._create_default_config()
            return cls._config
            
        except Exception as e:
            logger.error(f"Error al cargar la configuración: {str(e)}")
            cls._config = cls._create_default_config()
            return cls._config
    
    @classmethod
    def _create_default_config(cls):
        """
        Crea una configuración por defecto en caso de error.
        
        Returns:
            dict: Configuración por defecto.
        """
        default_config = {
            "frontend": {
                "singlePlayerMode": {
                    "enable": True,
                    "skipMenu": False
                },
                "display": {
                    "width": 800,
                    "height": 600,
                    "fullscreen": False,
                    "fpsLimit": 60
                },
                "level": {
                    "width": 400,
                    "height": 300
                }
            }
        }
        
        # Guardar la configuración por defecto
        try:
            with open(CONFIG_PATH, 'w') as config_file:
                json.dump(default_config, config_file, indent=2)
                logger.info(f"Configuración por defecto creada en: {CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error al guardar configuración por defecto: {str(e)}")
        
        return default_config
    
    @classmethod
    def get_config(cls):
        """
        Obtiene la configuración actual, cargándola si es necesario.
        
        Returns:
            dict: Configuración actual.
        """
        if cls._config is None:
            return cls.load_config()
        return cls._config
    
    @classmethod
    def get(cls, *keys, default=None):
        """
        Obtiene un valor de la configuración mediante una ruta de claves.
        
        Args:
            *keys: Secuencia de claves para acceder al valor (por ejemplo, "frontend", "singlePlayerMode", "enable")
            default: Valor por defecto si no se encuentra la clave
            
        Returns:
            El valor encontrado o el valor por defecto
        """
        if cls._config is None:
            cls.load_config()
            
        current = cls._config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    @classmethod
    def set(cls, value, *keys):
        """
        Establece un valor en la configuración mediante una ruta de claves.
        
        Args:
            value: Valor a establecer
            *keys: Secuencia de claves para acceder a la ubicación
            
        Returns:
            bool: True si se estableció correctamente, False en caso contrario
        """
        if cls._config is None:
            cls.load_config()
            
        if not keys:
            return False
            
        current = cls._config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        
        # Guardar cambios en el archivo
        try:
            with open(CONFIG_PATH, 'w') as config_file:
                json.dump(cls._config, config_file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error al guardar configuración: {str(e)}")
            return False
    
    # Métodos específicos para las configuraciones en uso
    
    @classmethod
    def is_single_player_enabled(cls):
        """
        Comprueba si el modo de un solo jugador está habilitado.
        
        Returns:
            bool: True si el modo de un solo jugador está habilitado, False en caso contrario.
        """
        return cls.get("frontend", "singlePlayerMode", "enable", default=True)
    
    @classmethod
    def should_skip_menu(cls):
        """
        Comprueba si se debe saltar el menú principal.
        
        Returns:
            bool: True si se debe saltar el menú, False en caso contrario.
        """
        return cls.get("frontend", "singlePlayerMode", "skipMenu", default=False)
    
    @classmethod
    def get_screen_width(cls):
        """
        Obtiene el ancho de la pantalla.
        
        Returns:
            int: Ancho de la pantalla en píxeles.
        """
        return cls.get("frontend", "display", "width", default=800)
    
    @classmethod
    def get_screen_height(cls):
        """
        Obtiene el alto de la pantalla.
        
        Returns:
            int: Alto de la pantalla en píxeles.
        """
        return cls.get("frontend", "display", "height", default=600)
    
    @classmethod
    def is_fullscreen(cls):
        """
        Comprueba si el juego debe ejecutarse en pantalla completa.
        
        Returns:
            bool: True si se debe usar pantalla completa, False en caso contrario.
        """
        return cls.get("frontend", "display", "fullscreen", default=False)
        
    @classmethod
    def get_fps_limit(cls):
        """
        Obtiene el límite de FPS configurado.
        
        Returns:
            int: Límite de FPS (fotogramas por segundo).
        """
        return cls.get("frontend", "display", "fpsLimit", default=60)
        
    @classmethod
    def get_level_width(cls):
        """
        Obtiene el ancho del área de juego lógica.
        
        Returns:
            int: Ancho del nivel en píxeles.
        """
        return cls.get("frontend", "level", "width", default=400)
        
    @classmethod
    def get_level_height(cls):
        """
        Obtiene el alto del área de juego lógica.
        
        Returns:
            int: Alto del nivel en píxeles.
        """
        return cls.get("frontend", "level", "height", default=300)
        
    @classmethod
    def get_level_aspect_ratio(cls):
        """
        Calcula la relación de aspecto del nivel.
        
        Returns:
            float: Relación de aspecto (ancho/alto)
        """
        width = cls.get_level_width()
        height = cls.get_level_height()
        return width / height if height > 0 else 1.0

# Inicializar la configuración al importar el módulo
Config.load_config() 