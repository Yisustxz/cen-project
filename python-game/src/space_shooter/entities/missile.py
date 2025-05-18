"""
Clase Missile - Representa los proyectiles disparados por el jugador.
"""
import pygame
from motor.sprite import GameObject
from space_shooter.core.constants import WHITE
from space_shooter.data.player_data import PlayerData

class Missile(GameObject):
    """Clase que representa un misil disparado por el jugador."""
    
    def __init__(self, x, y, player_id=None):
        """
        Inicializa un nuevo misil.
        
        Args:
            x: Posición x inicial del misil
            y: Posición y inicial del misil
            player_id: ID del jugador que disparó este misil (opcional)
        """
        # Inicializar primero sin imagen, pero con tipo "missile"
        super().__init__(x, y, None, obj_type="missile")
        
        # IDs para networking
        self.id = f"missile_default"
        self.player_id = player_id
        
        # Cargar datos de configuración
        missile_config = PlayerData.get_missile_data()
        
        # Ajustar el hitbox para hacerlo más pequeño
        self.hitbox_data = PlayerData.get_missile_hitbox_data()
        
        # Obtener velocidad desde la configuración
        missile_speed = PlayerData.get_missile_speed()
        
        # Guardar el daño que causa este misil
        self.damage = PlayerData.get_missile_damage()
        
        # Crear una simple imagen blanca para el misil
        # Usamos las dimensiones del hitbox para la imagen
        width = self.hitbox_data["width"] // 2  # Hacer la imagen más pequeña que el hitbox
        height = self.hitbox_data["height"] // 2
        
        self.image = pygame.Surface((width, height))
        self.original_image = self.image

        # Dibujar el misil como píxeles blancos
        for w in range(self.image.get_width()):
            for h in range(self.image.get_height()):
                self.image.set_at((w, h), WHITE)

        # En el nuevo sistema, no necesitamos ajustar x ya que el hitbox estará centrado en (x,y)
        # y el sprite se ajustará automáticamente según los offsets
        
        # Establecer velocidad usando los datos de configuración ajustados
        self.set_velocity(0, -missile_speed)

        # Aplicar hitbox con los datos de configuración ajustados
        self.set_hitbox_data(self.hitbox_data)
        
        # Para controlar si debe ser eliminado
        self.should_destroy = False
        self.has_hit = False

    def set_network_ids(self, missile_id, player_id=None):
        """
        Establece los IDs de red para este misil.
        
        Args:
            missile_id: ID único asignado a este misil
            player_id: ID del jugador que disparó este misil (opcional)
        """
        self.id = missile_id
        if player_id is not None:
            self.player_id = player_id

    def on_update(self):
        """
        Método llamado en cada actualización de frame.
        Verifica si el misil debe ser eliminado por salir de la pantalla.
        """
        # Eliminar el misil si sale por la parte superior de la pantalla
        if self.y < -50:
            # Si tiene referencia al juego, desregistrar el misil
            if self.game:
                self.game.unregister_object(self)
            self.kill()

    def on_collide(self, other_entity):
        """
        Maneja la colisión con otra entidad.
        
        Args:
            other_entity: La entidad con la que colisiona este misil
            
        Returns:
            bool: True si el misil debe ser destruido, False en caso contrario
        """
        # Si colisiona con un meteorito, el misil se destruye
        if other_entity.type == "meteor":
            # Si tiene referencia al juego, notificar la colisión
            if self.game:
                self.game.emit_event("missile_hit", {
                    "missile_id": self.id,
                    "player_id": self.player_id,
                    "hit_entity": other_entity,
                    "x": self.x,
                    "y": self.y
                })
                self.game.unregister_object(self)
            
            # Destruir el misil
            self.kill()
            return True
            
        # Para ahora, no destruir el misil si colisiona con otra cosa
        return False

    def get_damage(self):
        """Devuelve el daño que causa este misil."""
        return self.damage

    def should_destroy(self):
        """
        Indica si el misil debe ser destruido.
        Útil para manejar la destrucción desde fuera de la clase.
        
        Returns:
            bool: True si el misil debe ser destruido
        """
        # Si está fuera de la pantalla, se marca para destrucción
        return self.y < -50

    def on_game_event(self, event_type, data=None):
        """
        Maneja eventos emitidos por el juego.
        
        Args:
            event_type: Tipo de evento
            data: Datos asociados al evento (opcional)
            
        Returns:
            bool: True si el evento fue manejado, False en caso contrario
        """
        if event_type == "game_over":
            # Detener el movimiento
            self.set_velocity(0, 0)
            return True
            
        return False
