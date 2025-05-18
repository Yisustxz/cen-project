"""
Cliente de red para comunicación con el servidor de juego.
Encapsula toda la funcionalidad de comunicación gRPC.
"""
import grpc
import threading
import sys
from space_shooter.networking.generated import game_pb2, game_pb2_grpc
from config import Config
import time

class NetworkClient:
    """Cliente para comunicación con el servidor de juego."""
    
    def __init__(self, events_manager=None):
        """
        Inicializa el cliente de red.
        
        Args:
            events_manager: Referencia al gestor de eventos (opcional)
        """
        self.events_manager = events_manager
        self.player_id = None
        self.stub = None
        self.channel = None
        self.connected = False
        self.events_thread = None
        self.running = False
        self.player_name = "Player"  # Nombre por defecto
    
    def initialize(self):
        """
        Intenta inicializar la conexión con el servidor.
        Si no se puede conectar, muestra un error y termina el programa.
        
        Returns:
            bool: True si se conectó exitosamente
        """
        # Obtener configuración del servidor - sin fallbacks
        server_config = Config.get("frontend", "multiplayerMode", "server")
        if not server_config:
            print("Error: Configuración del servidor no encontrada. Verifica que 'frontend.multiplayerMode.server' exista en config.json")
            return False
            
        host = server_config.get("host")
        port = server_config.get("port")
        
        if not host or not port:
            print("Error: Configuración incompleta del servidor. Verifica que 'host' y 'port' estén definidos en frontend.multiplayerMode.server en config.json")
            return False
        
        print(f"Intentando conectar al servidor en {host}:{port}...")
        
        try:
            # Crear canal y stub
            self.channel = grpc.insecure_channel(f"{host}:{port}")
            self.stub = game_pb2_grpc.GameServiceStub(self.channel)
            
            # Probar conexión con timeout
            grpc.channel_ready_future(self.channel).result(timeout=5)
            
            # Si llegamos aquí, la conexión fue exitosa
            print("Canal establecido con éxito. Intentando autenticación...")
            success = self.connect(self.player_name)
            
            if not success:
                print("Error al autenticar con el servidor.")
                return False
                
            return True
            
        except grpc.FutureTimeoutError:
            print(f"Error: Timeout al conectar al servidor en {host}:{port}")
            return False
        except grpc.RpcError as e:
            print(f"Error de comunicación con el servidor: {e.code()}: {e.details()}")
            return False
        except Exception as e:
            print(f"Error inesperado al conectar: {str(e)}")
            return False
    
    def connect(self, player_name):
        """
        Realiza la autenticación con el servidor.
        
        Args:
            player_name: Nombre del jugador
            
        Returns:
            bool: True si la autenticación fue exitosa
        """
        if not self.stub:
            return False
            
        try:
            self.player_name = player_name
            
            # Crear solicitud de conexión
            request = game_pb2.ConnectRequest(player_name=player_name)
            
            # Enviar solicitud
            response = self.stub.Connect(request)
            
            # Verificar respuesta
            if not response.success:
                print(f"Error durante autenticación: {response.error_message}")
                return False
                
            # Guardar ID asignado
            self.player_id = response.player_id
            self.connected = True
            
            print(f"Conectado exitosamente al servidor con ID: {self.player_id}")
            
            # Iniciar hilo para eventos
            self._start_events_thread()
            
            # Esperar un breve momento para que el servidor actualice su estado
            time.sleep(0.5)

            return True
            
        except grpc.RpcError as e:
            print(f"Error al conectar: {e.code()}: {e.details()}")
            return False
        except Exception as e:
            print(f"Error inesperado durante la conexión: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def disconnect(self):
        """Desconecta del servidor."""
        if not self.connected:
            return
            
        try:
            # Detener el hilo de eventos
            self.running = False
            if self.events_thread and self.events_thread.is_alive():
                self.events_thread.join(timeout=1.0)
            
            # Enviar evento de desconexión si es posible
            if self.stub and self.player_id:
                try:
                    # Crear una solicitud de desconexión con la estructura correcta
                    disconnect_request = game_pb2.ClientRequest(
                        player_id=self.player_id,
                        disconnect=True
                    )
                    
                    # También notificar la desconexión con un evento estructurado correctamente
                    player_disconnect = game_pb2.PlayerDisconnectEvent(
                        player_id=self.player_id,
                        player_name=self.player_name
                    )
                    
                    event = game_pb2.GameEvent(
                        event_type="player_disconnect",
                        player_disconnect=player_disconnect
                    )
                    
                    self.stub.SendEvent(event)
                except Exception as e:
                    print(f"No se pudo enviar evento de desconexión: {e}")
            
            # Cerrar canal
            if self.channel:
                self.channel.close()
            
            self.connected = False
            self.player_id = None
            print("Desconectado del servidor")
            
        except Exception as e:
            print(f"Error al desconectar: {e}")
    
    def send_player_position(self, x, y, speed_x, speed_y):
        """
        Envía la posición del jugador al servidor.
        
        Args:
            x: Posición X
            y: Posición Y
            speed_x: Velocidad X
            speed_y: Velocidad Y
        """
        if not self.connected or not self.stub:
            return
            
        try:
            # Ahora podemos usar el PlayerPositionEvent correctamente desde el proto actualizado
            position = game_pb2.Vector2D(x=x, y=y)
            velocity = game_pb2.Vector2D(x=speed_x, y=speed_y)
            
            # Crear evento de posición usando el campo dedicado
            player_position = game_pb2.PlayerPositionEvent(
                player_id=self.player_id,
                position=position,
                velocity=velocity
            )
            
            # Crear evento usando la estructura de oneof correcta con el nuevo campo
            event = game_pb2.GameEvent(
                event_type="player_position",
                player_position=player_position
            )
            
            # Enviar evento
            self.stub.SendEvent(event)
            
        except Exception as e:
            print(f"Error al enviar posición: {e}")
    
    def request_game_state(self):
        """
        Solicita el estado actual del juego.
        
        Returns:
            GameState: El estado del juego o None si hubo un error
        """
        if not self.connected or not self.stub:
            print("Error: No se puede solicitar el estado del juego porque no hay conexión con el servidor")
            return None
            
        try:
            print(f"Solicitando estado del juego para el jugador {self.player_id}...")
            
            # Crear solicitud usando el campo get_game_state
            request = game_pb2.ClientRequest(
                player_id=self.player_id,
                get_game_state=True
            )
            
            # Llamar al método GetGameState (el único que devuelve directamente un GameState)
            response_iterator = self.stub.GetGameState(iter([request]))
            
            # Obtener el primer resultado (o None si no hay)
            try:
                game_state = next(response_iterator)
                
                # Verificar si el estado contiene jugadores
                player_count = 0
                if game_state and game_state.players and hasattr(game_state.players, 'players'):
                    player_count = len(game_state.players.players)
                    
                print(f"Estado del juego recibido con {player_count} jugadores")
                
                # Imprimir información de cada jugador para depuración
                if player_count > 0:
                    print("Jugadores en el estado:")
                    for player in game_state.players.players:
                        print(f"  - ID: {player.player_id}, Nombre: {player.name}")
                
                return game_state
            except StopIteration:
                print("Error: No se recibió respuesta del servidor al solicitar el estado del juego")
                return None
                
        except grpc.RpcError as e:
            print(f"Error RPC al solicitar estado del juego: {e.code()}: {e.details()}")
            return None
        except Exception as e:
            print(f"Error inesperado al solicitar estado del juego: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _start_events_thread(self):
        """Inicia el hilo para recibir eventos del servidor."""
        self.running = True
        self.events_thread = threading.Thread(
            target=self._events_listener,
            daemon=True
        )
        self.events_thread.start()
    
    def _events_listener(self):
        """Función del hilo que escucha eventos del servidor."""
        if not self.connected or not self.stub:
            return
            
        try:
            # Crear solicitud de suscripción
            request = game_pb2.ClientRequest(
                player_id=self.player_id
            )
            
            # Iniciar stream de eventos
            events_stream = self.stub.SubscribeToEvents(request)
            print("Suscrito al stream de eventos del servidor")
            
            # Procesar eventos mientras se ejecuta
            while self.running:
                try:
                    # Recibir próximo evento con timeout
                    event = next(events_stream)
                    
                    # Procesar evento recibido
                    if self.events_manager:
                        self.events_manager.handle_server_event(event)
                    
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.CANCELLED:
                        break
                    print(f"Error en stream de eventos: {e}")
                    break
                    
        except Exception as e:
            print(f"Error en hilo de eventos: {e}")
            self.connected = False 