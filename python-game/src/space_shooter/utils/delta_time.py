"""
Utilidad para manejar el tiempo delta entre frames para actualizar movimientos
independientes de la velocidad de cuadros (FPS).
"""
import time

class DeltaTime:
    """
    Clase estática para manejar el tiempo entre frames.
    
    Permite que el movimiento y las actualizaciones sean consistentes
    independientemente de la velocidad de cuadros real.
    """
    # Tiempo del último frame
    _last_time = 0
    
    # Delta time actual (tiempo entre frames)
    _delta = 0
    
    # Delta time máximo para evitar saltos extremos
    _max_delta = 0.2  # 200ms máximo para evitar saltos grandes en caso de lag
    
    # FPS base para cálculos
    _base_fps = 60
    
    @classmethod
    def init(cls):
        """Inicializa el sistema de tiempo delta."""
        cls._last_time = time.time()
        cls._delta = 0
    
    @classmethod
    def update(cls):
        """
        Actualiza el delta time basado en el tiempo desde el último frame.
        Debe llamarse una vez por frame, preferiblemente al inicio de cada ciclo.
        """
        current_time = time.time()
        cls._delta = min(current_time - cls._last_time, cls._max_delta)
        cls._last_time = current_time
    
    @classmethod
    def get_delta(cls):
        """
        Obtiene el tiempo delta entre frames en segundos.
        
        Returns:
            float: Tiempo en segundos desde el último frame
        """
        return cls._delta
    
    @classmethod
    def get_fixed_delta(cls):
        """
        Obtiene el tiempo delta fijo basado en los FPS base.
        Útil para comparar con el delta real.
        
        Returns:
            float: Tiempo fijo en segundos (1/base_fps)
        """
        return 1.0 / cls._base_fps
    
    @classmethod
    def get_scale_factor(cls):
        """
        Obtiene el factor de escala para ajustar valores basados en FPS reales vs. esperados.
        
        Returns:
            float: Factor de escala para ajustar valores
        """
        fixed_delta = cls.get_fixed_delta()
        if fixed_delta == 0:
            return 1.0
        return cls._delta / fixed_delta
    
    @classmethod
    def scale_value(cls, value):
        """
        Escala un valor basado en el delta time actual.
        
        Args:
            value: Valor a escalar
            
        Returns:
            float: Valor escalado según el tiempo delta
        """
        return value * cls._delta
    
    @classmethod
    def scale_value_per_second(cls, value_per_second):
        """
        Convierte un valor por segundo en un valor por frame según el delta time.
        
        Args:
            value_per_second: Valor por segundo
            
        Returns:
            float: Valor para el frame actual
        """
        return value_per_second * cls._delta 