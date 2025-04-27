import sys
import os
import grpc

# Añadir la carpeta 'generated' al PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '../generated'))

import grpc
import game_pb2
import game_pb2_grpc
def run():
    # Conectar al servidor gRPC (por ejemplo localhost:50051)
    channel = grpc.insecure_channel('localhost:50051')
    stub = game_pb2_grpc.GameServiceStub(channel)

    # Crear una solicitud
    request = game_pb2.PlayerInput(player_id="player1", action="move")

    # Llamar al método SendInput en el servidor
    response = stub.SendInput(request)
    print("Server responded: ", response.message)

if __name__ == '__main__':
    run()
