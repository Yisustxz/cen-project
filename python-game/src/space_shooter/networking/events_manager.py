"""
Gestor de eventos para comunicación entre el juego y la red.
"""
import threading
from space_shooter.networking.generated import game_pb2

class NetworkEventsManager:
    """
    Gestiona eventos entre el servidor y el juego.
    Encapsula la lógica de conversión entre eventos de red y eventos del juego.
    """
    
    def __init__(self, game=None, client=None):
        """
        Inicializa el gestor de eventos.
        
        Args:
            game: Referencia al juego (opcional)
            client: Referencia al cliente de red (opcional)
        """
        self.game = game
        self.client = client
        self.lock = threading.Lock()
    
    def set_game(self, game):
        """Establece la referencia al juego."""
        self.game = game
    
    def set_client(self, client):
        """Establece la referencia al cliente de red."""
        self.client = client
        
        # Si el cliente no tiene referencia a este gestor, establecerla
        if client and not client.events_manager:
            client.events_manager = self
    
    def handle_server_event(self, notification_event):
        """
        Procesa eventos recibidos del servidor.
        
        Args:
            notification_event: NotificationEvent recibido del servidor
        """
        if not self.game:
            return
        
        # El servidor ahora envía NotificationEvent que contiene un GameEvent
        if not hasattr(notification_event, 'event') or not notification_event.event:
            print("Advertencia: Evento recibido sin datos")
            return
            
        # Extraer el evento real
        event = notification_event.event
        event_type = event.event_type
        
        # Guardar el tipo de evento actual para referencia en los handlers
        self._current_event_type = event_type
        
        # Manejar diferentes tipos de eventos basados en el tipo y el campo específico
        if event_type == "player_connect" and hasattr(event, 'player_connect'):
            data = event.player_connect
            self._handle_player_connect(data)
        
        elif event_type == "player_disconnect" and hasattr(event, 'player_disconnect'):
            data = event.player_disconnect
            self._handle_player_disconnect(data)
        
        elif event_type == "player_position" and hasattr(event, 'player_position'):
            data = event.player_position
            self._handle_player_position(data)
        
        elif event_type == "meteor_destroyed" and hasattr(event, 'meteor_destroyed'):
            data = event.meteor_destroyed
            self._handle_meteor_destroyed(data)
            
        elif event_type == "missile_fired" and hasattr(event, 'meteor_destroyed'):
            # Reutilizamos meteor_destroyed para misiles
            data = event.meteor_destroyed
            self._handle_meteor_destroyed(data)
        
        elif event_type == "score_update" and hasattr(event, 'score_update'):
            data = event.score_update
            self._handle_score_update(data)
            
        elif event_type == "meteor_created" and hasattr(event, 'meteor_created'):
            data = event.meteor_created
            self._handle_meteor_created(data)
        
        # Si no tiene un campo específico, intentar usar campos genéricos
        else:
            print(f"Evento de tipo desconocido: {event_type}")
            
        # Limpiar la referencia al tipo de evento actual
        self._current_event_type = None
    
    def _handle_player_connect(self, player_connect_data):
        """Maneja un evento de conexión de jugador."""
        if not hasattr(player_connect_data, 'player_id') or not hasattr(player_connect_data, 'player_name'):
            return
            
        self.game.emit_event("online_player_connected", {
            "player_id": player_connect_data.player_id,
            "player_name": player_connect_data.player_name,
            "x": 0,  # Posición por defecto hasta que se reciba una actualización
            "y": 0
        })
    
    def _handle_player_disconnect(self, player_disconnect_data):
        """Maneja un evento de desconexión de jugador."""
        if not hasattr(player_disconnect_data, 'player_id'):
            return
            
        self.game.emit_event("online_player_disconnected", {
            "player_id": player_disconnect_data.player_id
        })
    
    def _handle_meteor_destroyed(self, meteor_destroyed_data):
        """Maneja un evento de meteorito destruido o misil disparado."""
        if not hasattr(meteor_destroyed_data, 'player_id'):
            return
        
        # Verificar el tipo de evento real basado en el event_type padre
        parent_event = getattr(self, '_current_event_type', None)
        
        # Si es un evento de misil disparado
        if parent_event == "missile_fired":
            self.game.emit_event("online_missile_fired", {
                "player_id": meteor_destroyed_data.player_id,
                "missile_id": meteor_destroyed_data.meteor_id
            })
            return
            
        # Si es un evento normal de meteorito destruido
        self.game.emit_event("online_meteor_destroyed", {
            "meteor_id": meteor_destroyed_data.meteor_id,
            "player_id": getattr(meteor_destroyed_data, 'player_id', 0)
        })
    
    def _handle_score_update(self, score_update_data):
        """Maneja un evento de actualización de puntuación."""
        if not hasattr(score_update_data, 'player_id') or not hasattr(score_update_data, 'score_delta'):
            return
            
        self.game.emit_event("online_score_update", {
            "player_id": score_update_data.player_id,
            "score_delta": score_update_data.score_delta
        })
    
    def _handle_player_position(self, player_position_data):
        """
        Maneja un evento de posición de jugador.
        
        Args:
            player_position_data: Datos de PlayerPositionEvent
        """
        if not hasattr(player_position_data, 'player_id') or not hasattr(player_position_data, 'position'):
            return
            
        position = player_position_data.position
        velocity = player_position_data.velocity
        
        # Emitir evento al juego
        self.game.emit_event("online_player_position", {
            "player_id": player_position_data.player_id,
            "x": position.x,
            "y": position.y,
            "speed_x": velocity.x if velocity else 0,
            "speed_y": velocity.y if velocity else 0
        })
    
    def on_player_position_changed(self, player, force_stop=False):
        """
        Notifica al servidor sobre el cambio de posición del jugador.
        
        Args:
            player: Objeto del jugador local
            force_stop: Si es True, indica que el jugador se detuvo por colisión con el borde
        """
        if not self.client or not self.client.connected:
            return
            
        try:
            # Ahora podemos usar el PlayerPositionEvent correctamente
            # Crear vectors para posición y velocidad
            position = game_pb2.Vector2D(x=player.x, y=player.y)
            
            # Si force_stop está activo, aseguramos que la velocidad sea 0
            if force_stop:
                velocity = game_pb2.Vector2D(x=0, y=0)
                print(f"Forzando STOP en el borde para jugador {self.client.player_id}")
            else:
                velocity = game_pb2.Vector2D(
                    x=player.speed_x if hasattr(player, 'speed_x') else 0, 
                    y=player.speed_y if hasattr(player, 'speed_y') else 0
                )
            
            # Crear evento de posición usando el campo dedicado
            player_position = game_pb2.PlayerPositionEvent(
                player_id=self.client.player_id,
                position=position,
                velocity=velocity
            )
            
            # Crear evento usando la estructura oneof correcta con el nuevo campo
            event = game_pb2.GameEvent(
                event_type="player_position",
                player_position=player_position
            )
            
            # Enviar el evento
            self.client.stub.SendEvent(event)
        except Exception as e:
            print(f"Error al enviar posición del jugador: {e}")
    
    def on_player_fired_missile(self, data):
        """
        Notifica al servidor sobre un misil disparado.
        
        Args:
            data: Datos del disparo con x, y, player_id
        """
        if not self.client or not self.client.connected:
            return
            
        try:
            # Verificar que tengamos los datos necesarios
            if 'x' not in data or 'y' not in data or 'player_id' not in data:
                return
            
            # Crear Vector2D para la posición del misil
            position = game_pb2.Vector2D(
                x=data['x'],
                y=data['y']
            )
            
            # Crear evento de misil disparado usando MeteorDestroyedEvent como vehículo
            # (reutilizamos otro tipo existente ya que no hay MissileFiredEvent)
            missile_event = game_pb2.MeteorDestroyedEvent(
                meteor_id=0,  # Usamos 0 como ID temporal
                player_id=data['player_id']
            )
            
            # Crear evento con tipo personalizado
            event = game_pb2.GameEvent(
                event_type="missile_fired",
                meteor_destroyed=missile_event
            )
            
            # Enviar el evento
            self.client.stub.SendEvent(event)
            print(f"Enviado evento de misil disparado por jugador {data['player_id']}")
            
        except Exception as e:
            print(f"Error al enviar evento de disparo de misil: {e}")

    def _handle_meteor_created(self, meteor_created_data):
        """
        Maneja un evento de creación de meteorito.
        
        Args:
            meteor_created_data: Datos del meteorito creado
        """
        if not hasattr(meteor_created_data, 'meteor_id') or not hasattr(meteor_created_data, 'position'):
            print("Error: Datos incompletos en evento meteor_created")
            return
            
        # Extraer datos del meteorito
        position = meteor_created_data.position
        velocity = meteor_created_data.velocity if hasattr(meteor_created_data, 'velocity') else None
        
        # Emitir evento al juego con todos los datos necesarios
        self.game.emit_event("online_meteor_created", {
            "meteor_id": meteor_created_data.meteor_id,
            "type": meteor_created_data.meteor_type,
            "x": position.x if position else 0,
            "y": position.y if position else 0,
            "angle": getattr(meteor_created_data, 'angle', 0),
            "rotation_speed": getattr(meteor_created_data, 'rotation_speed', 0),
            "speed_x": velocity.x if velocity else 0,
            "speed_y": velocity.y if velocity else 0
        })
        print(f"Meteorito remoto recibido: ID {meteor_created_data.meteor_id}, Tipo {meteor_created_data.meteor_type}") 