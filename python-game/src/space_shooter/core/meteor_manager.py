"""
Gestor de meteoritos para el juego Space Shooter.
Encapsula toda la lógica relacionada con la creación y gestión de meteoritos.
"""
import random
from space_shooter.entities.meteor import Meteor
from space_shooter.data.meteor_data import MeteorData
from space_shooter.core.constants import METEOR_SPAWN_FREQUENCY
from config import Config

class MeteorManager:
    """
    Clase encargada de gestionar los meteoritos en el juego.
    
    Responsabilidades:
    - Creación de meteoritos con diferentes tipos y propiedades
    - Gestión del tiempo entre meteoritos
    - Ajuste de dificultad (frecuencia, tipos)
    """
    
    def __init__(self, game):
        """
        Inicializa el gestor de meteoritos.
        
        Args:
            game: Referencia al juego principal (SpaceShooterGame)
        """
        self.game = game
        self.resource_manager = game.resource_manager
        self.spawn_timer = 0
        self.spawn_frequency = METEOR_SPAWN_FREQUENCY
        
        # Variables para ajuste de dificultad
        self.difficulty_factor = 1.0
        self.min_spawn_frequency = 30  # Mínimo tiempo entre meteoritos
        self.difficulty_increase_rate = 0.002  # Aumento de dificultad por frame
        
        # Pesos de probabilidad para diferentes categorías de meteoritos
        self.meteor_category_weights = {
            "big": 20,     # Meteoritos grandes: 20%
            "medium": 35,  # Meteoritos medianos: 35%
            "small": 30,   # Meteoritos pequeños: 30%
            "tiny": 15     # Meteoritos diminutos: 15%
        }
        
        # Pesos de probabilidad para colores
        self.color_weights = {
            "brown": 60,   # Marrón: 60%
            "grey": 40     # Gris: 40%
        }
    
    def update(self):
        """
        Actualiza el gestor de meteoritos.
        Llamado en cada frame por SpaceShooterGame.
        """
        # Actualizar contador de creación
        self.spawn_timer += 1
        
        # Aumentar dificultad gradualmente
        # Comentado hasta que se implemente la señal del servidor
        # if self.spawn_frequency > self.min_spawn_frequency:
        #     self.spawn_frequency -= self.difficulty_increase_rate
        
        # Crear un nuevo meteorito si es el momento
        if self.spawn_timer >= self.spawn_frequency:
            self.create_meteor()
            self.spawn_timer = 0
    
    def reset(self):
        """Reinicia el gestor de meteoritos a sus valores iniciales."""
        self.spawn_timer = 0
        self.spawn_frequency = METEOR_SPAWN_FREQUENCY
        self.difficulty_factor = 1.0
    
    def create_meteor(self, meteor_type=None, position=None):
        """
        Crea un meteorito y lo registra en el motor del juego.
        
        Args:
            meteor_type: Tipo específico de meteorito (opcional)
            position: Posición inicial del meteorito (opcional)
            
        Returns:
            Meteor: El meteorito creado, o None si hubo un error
        """
        print("Creando un nuevo meteorito...")
        try:
            # Si no se especifica tipo, seleccionar uno aleatorio
            if meteor_type is None:
                meteor_type = self._select_random_meteor_type()
            
            # Obtener datos para el tipo de meteorito
            meteor_data = MeteorData.get_type_data(meteor_type)
            
            # Cargar imagen del meteorito
            meteor_img = MeteorData.load_meteor_image(self.resource_manager, meteor_type)
            
            # Determinar propiedades aleatorias del meteorito
            meteor_properties = self._determine_meteor_properties(meteor_data, position)
            
            # Crear el meteorito con la imagen, tipo, datos y propiedades
            meteor = Meteor(
                meteor_img, 
                meteor_type, 
                meteor_data,
                meteor_properties["position"],
                meteor_properties["speed"],
                meteor_properties["rotation"]
            )
            
            # Registrar el meteorito en el motor
            self.game.register_object(meteor)
            
            print(f"Meteorito tipo {meteor_type} creado correctamente.")
            return meteor
        except Exception as e:
            print(f"Error al crear meteorito: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _determine_meteor_properties(self, meteor_data, position=None):
        """
        Determina todas las propiedades aleatorias para un meteorito.
        
        Args:
            meteor_data: Datos de configuración del tipo de meteorito
            position: Posición inicial opcional (x, y)
            
        Returns:
            dict: Diccionario con todas las propiedades aleatorias
        """
        # Determinar posición si no se proporciona
        if position is None:
            # Usar ancho del nivel en lugar del ancho del juego
            level_width = Config.get_level_width()
            x = random.randint(0, level_width)
            y = -100  # Inicio por encima de la pantalla
            position = (x, y)
        
        # Obtener rangos de velocidad desde la configuración del meteoro
        speed_x_range = meteor_data.get("speed_x_range", (-1, 1))
        speed_y_range = meteor_data.get("speed_y_range", (1, 3))
        rotation_range = meteor_data.get("rotation_speed_range", (-3, 3))
        
        # Determinar velocidades aleatorias
        speed_x = random.uniform(speed_x_range[0], speed_x_range[1])
        speed_y = random.uniform(speed_y_range[0], speed_y_range[1])
        
        # Determinar rotación aleatoria
        angle = random.randint(0, 360)
        rotation_speed = random.uniform(rotation_range[0], rotation_range[1])
        
        # Devolver todas las propiedades
        return {
            "position": position,
            "speed": (speed_x, speed_y),
            "rotation": (angle, rotation_speed)
        }
    
    def on_meteor_destroyed(self, data):
        """
        Maneja el evento de destrucción de un meteorito.
        
        Args:
            data: Datos del evento con points, x, y, meteor
        """
        # Posible lógica adicional aquí, como crear meteoritos secundarios,
        # ajustar patrones de generación, etc.
        pass
    
    def _select_random_meteor_type(self):
        """
        Selecciona un tipo de meteorito aleatorio basado en los pesos de probabilidad.
        
        Returns:
            str: Tipo de meteorito individual (por ejemplo, "brown_big_1", "grey_small_2")
        """
        # Primero seleccionar categoría de tamaño
        categories = list(self.meteor_category_weights.keys())
        size_weights = [self.meteor_category_weights[cat] for cat in categories]
        selected_category = random.choices(categories, weights=size_weights, k=1)[0]
        
        # Usar el sistema de categorías de MeteorData para obtener un tipo aleatorio
        # dentro de la categoría seleccionada
        return MeteorData.get_random_type(selected_category)
    
    # La función increase_difficulty está comentada para ser activada solo
    # cuando se reciba una señal del servidor
    #
    # def increase_difficulty(self, amount=0.1):
    #     """
    #     Aumenta la dificultad del juego.
    #     
    #     Args:
    #         amount: Cantidad de aumento de dificultad (valor entre 0.1 y 1.0)
    #     """
    #     self.difficulty_factor += amount
    #     
    #     # Ajustar pesos hacia meteoritos más pequeños y rápidos
    #     if self.meteor_category_weights["big"] > 5:
    #         self.meteor_category_weights["big"] -= amount * 10
    #         self.meteor_category_weights["tiny"] += amount * 10
    #     
    #     # Ajustar pesos hacia más meteoritos grises (más resistentes)
    #     if self.color_weights["grey"] < 60:
    #         self.color_weights["grey"] += amount * 10
    #         self.color_weights["brown"] -= amount * 10
    