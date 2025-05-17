"""
Datos de configuración del jugador y los misiles.
Este módulo contiene las definiciones para el jugador y los misiles,
cargados desde el archivo de configuración.
"""
import json

CONFIG_PATH = "entities_config.json"

class PlayerData:
    """Clase que proporciona acceso a los datos del jugador y misiles"""
    _instance = None
    _player_config = None
    _missile_config = None

    @classmethod
    def get_instance(cls):
        """Retorna la instancia singleton de PlayerData"""
        if cls._instance is None:
            cls._instance = PlayerData()
        return cls._instance

    def __init__(self):
        """Constructor para PlayerData. Carga la configuración del jugador y misiles."""
        if PlayerData._instance is not None:
            raise Exception("Esta clase es un singleton. Use get_instance().")
            
        try:
            with open(CONFIG_PATH, 'r') as config_file:
                config_data = json.load(config_file)
                self._player_config = config_data["player"]
                self._missile_config = config_data["missile"]
        except Exception as e:
            print(f"Error cargando configuración del jugador/misiles: {e}")
            # Valores por defecto
            self._player_config = {
                "speed": 250,
                "lives": 3,
                "fire_delay": 0.5,
                "damage_time": 2.0,
                "width": 40,
                "height": 40,
                "offset_x": 0,
                "offset_y": 0
            }
            
            self._missile_config = {
                "speed": 500,
                "damage": 1,
                "width": 10,
                "height": 20,
                "offset_x": 0,
                "offset_y": 0
            }

    # Métodos estáticos para uso desde cualquier parte del código
    @classmethod
    def get_player_data(cls):
        """Retorna los datos completos del jugador"""
        instance = cls.get_instance()
        return instance._player_config

    @classmethod
    def get_missile_data(cls):
        """Retorna los datos completos del misil"""
        instance = cls.get_instance()
        return instance._missile_config

    # Métodos para obtener datos del jugador
    @classmethod
    def get_player_speed(cls):
        """Retorna la velocidad del jugador"""
        instance = cls.get_instance()
        return instance._player_config["speed"]
    
    @classmethod
    def get_player_lives(cls):
        """Retorna la cantidad de vidas del jugador"""
        instance = cls.get_instance()
        return instance._player_config["lives"]
    
    @classmethod
    def get_player_fire_delay(cls):
        """Retorna el tiempo de enfriamiento entre disparos en segundos"""
        instance = cls.get_instance()
        return instance._player_config["fire_delay"]
    
    @classmethod
    def get_player_damage_time(cls):
        """Retorna el tiempo de invulnerabilidad después de recibir daño en segundos"""
        instance = cls.get_instance()
        return instance._player_config["damage_time"]
    
    @classmethod
    def get_player_hitbox_data(cls):
        """Retorna los datos del hitbox del jugador"""
        instance = cls.get_instance()
        return {
            "width": instance._player_config.get("width", instance._player_config.get("hitbox_width", 40)),
            "height": instance._player_config.get("height", instance._player_config.get("hitbox_height", 40)),
            "offset_x": instance._player_config.get("offset_x", 0),
            "offset_y": instance._player_config.get("offset_y", 0)
        }
    
    # Métodos para obtener datos del misil
    @classmethod
    def get_missile_speed(cls):
        """Retorna la velocidad del misil"""
        instance = cls.get_instance()
        return instance._missile_config["speed"]
    
    @classmethod
    def get_missile_damage(cls):
        """Retorna el daño causado por el misil"""
        instance = cls.get_instance()
        return instance._missile_config["damage"]
    
    @classmethod
    def get_missile_hitbox_data(cls):
        """Retorna los datos del hitbox del misil"""
        instance = cls.get_instance()
        return {
            "width": instance._missile_config.get("width", instance._missile_config.get("hitbox_width", 10)),
            "height": instance._missile_config.get("height", instance._missile_config.get("hitbox_height", 20)),
            "offset_x": instance._missile_config.get("offset_x", 0),
            "offset_y": instance._missile_config.get("offset_y", 0)
        } 