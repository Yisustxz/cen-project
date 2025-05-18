package server

import (
	"context"
	"fmt"
	"net"
	"time"

	"google.golang.org/grpc"

	"github.com/Yisustxz/cen-project/backend/types"
	pb "github.com/Yisustxz/cen-project/backend/internal/service"
)

// GameServiceImpl implementa la lógica de negocio del servidor
type GameServiceImpl struct {
	pb.UnimplementedGameServiceServer
	server *types.GameServer
}

// NewGameServiceImpl crea una nueva instancia del servicio del juego
func NewGameServiceImpl(server *types.GameServer) *GameServiceImpl {
	return &GameServiceImpl{
		server: server,
	}
}

// BroadcastEvent envía un evento a todos los clientes conectados
func (s *GameServiceImpl) BroadcastEvent(event *pb.GameEvent) {
	notification := &pb.NotificationEvent{
		Event:     event,
		Timestamp: int32(time.Now().Unix()),
	}

	s.server.PlayersMutex.RLock()
	defer s.server.PlayersMutex.RUnlock()

	for playerID, player := range s.server.Players {
		if !player.IsActive {
			continue
		}

		player.StreamMutex.RLock()
		if player.EventStream != nil && player.EventStream.Active {
			if err := player.EventStream.Stream.Send(notification); err != nil {
				s.server.Logger.LogError(
					"Error enviando notificación al jugador", 
					err,
				)
				// Marcar como inactivo para limpiarlo más tarde
				player.EventStream.Active = false
			} else {
				// Actualizar tiempo de última actividad
				player.EventStream.LastSeen = time.Now()
				s.server.Logger.LogMessage(
					fmt.Sprintf("Notificación enviada al jugador %d", playerID),
				)
			}
		}
		player.StreamMutex.RUnlock()
	}
}

// CleanupInactiveStreams elimina los streams inactivos
func (s *GameServiceImpl) CleanupInactiveStreams() {
	cutoff := time.Now().Add(-5 * time.Minute)
	
	s.server.PlayersMutex.RLock()
	defer s.server.PlayersMutex.RUnlock()
	
	for playerID, player := range s.server.Players {
		player.StreamMutex.Lock()
		if player.EventStream != nil && 
		   (!player.EventStream.Active || player.EventStream.LastSeen.Before(cutoff)) {
			player.EventStream = nil
			s.server.Logger.LogMessage(
				fmt.Sprintf("Stream inactivo eliminado para el jugador %d", playerID),
			)
		}
		player.StreamMutex.Unlock()
	}
}

// Start inicia el servidor gRPC
func (s *GameServiceImpl) Start(address string) error {
	lis, err := net.Listen("tcp", address)
	if err != nil {
		return err
	}

	grpcServer := grpc.NewServer()
	pb.RegisterGameServiceServer(grpcServer, s)

	s.server.Logger.LogMessage(fmt.Sprintf("Servidor iniciado en %s", address))

	// Iniciamos el servidor en una goroutine para no bloquear
	go func() {
		if err := grpcServer.Serve(lis); err != nil {
			s.server.Logger.LogError("Error en el servidor", err)
		}
	}()

	// Iniciamos una goroutine para limpiar streams inactivos periódicamente
	go func() {
		ticker := time.NewTicker(1 * time.Minute)
		defer ticker.Stop()
		for {
			<-ticker.C
			s.CleanupInactiveStreams()
		}
	}()

	return nil
}

// Connect maneja la solicitud de conexión de un nuevo jugador
func (s *GameServiceImpl) Connect(ctx context.Context, req *pb.ConnectRequest) (*pb.ConnectResponse, error) {
	s.server.PlayersMutex.Lock()
	playerID := s.server.NextPlayerID
	s.server.NextPlayerID++

	newPlayer := &types.Player{
		ID:       playerID,
		Name:     req.PlayerName,
		Position: &pb.Vector2D{X: 400, Y: 500}, // Posición inicial
		Score:    0,
		IsActive: true,
	}

	s.server.Players[playerID] = newPlayer
	s.server.PlayersMutex.Unlock()

	s.server.Logger.LogMessage(fmt.Sprintf("Jugador conectado: %s (ID: %d)", req.PlayerName, playerID))

	// Actualizar el estado del juego
	s.updateGameState()

	// Notificar a todos los clientes conectados sobre el nuevo jugador
	connectEvent := &pb.GameEvent{
		EventType: "player_connect",
		EventData: &pb.GameEvent_PlayerConnect{
			PlayerConnect: &pb.PlayerConnectEvent{
				PlayerId:   playerID,
				PlayerName: req.PlayerName,
			},
		},
	}
	s.BroadcastEvent(connectEvent)

	return &pb.ConnectResponse{
		PlayerId:     playerID,
		Success:      true,
		ErrorMessage: "",
	}, nil
}

// SubscribeToEvents implementa la suscripción a eventos para los clientes
func (s *GameServiceImpl) SubscribeToEvents(req *pb.ClientRequest, stream pb.GameService_SubscribeToEventsServer) error {
	playerID := req.PlayerId

	// Verificar que el jugador exista
	s.server.PlayersMutex.RLock()
	player, exists := s.server.Players[playerID]
	s.server.PlayersMutex.RUnlock()

	if !exists || !player.IsActive {
		return fmt.Errorf("el jugador con ID %d no existe o está inactivo", playerID)
	}

	// Crear una nueva suscripción
	eventStream := &types.EventStream{
		Stream:   stream,
		LastSeen: time.Now(),
		Active:   true,
	}

	// Registrar la suscripción en el jugador
	player.StreamMutex.Lock()
	player.EventStream = eventStream
	player.StreamMutex.Unlock()

	s.server.Logger.LogMessage(fmt.Sprintf("Jugador %d suscrito a eventos", playerID))

	// Mantener la conexión abierta
	<-stream.Context().Done()

	// Al cerrar la conexión, marcar como inactivo
	player.StreamMutex.Lock()
	if player.EventStream != nil {
		player.EventStream.Active = false
	}
	player.StreamMutex.Unlock()

	s.server.Logger.LogMessage(fmt.Sprintf("Jugador %d desuscrito de eventos", playerID))
	return nil
}

// SendEvent maneja los eventos enviados por los clientes
func (s *GameServiceImpl) SendEvent(ctx context.Context, event *pb.GameEvent) (*pb.ServerResponse, error) {
	// Procesar el evento según su tipo
	switch event.EventType {
	case "player_disconnect":
		if playerDisconnect, ok := event.GetEventData().(*pb.GameEvent_PlayerDisconnect); ok {
			playerID := playerDisconnect.PlayerDisconnect.PlayerId
			s.handlePlayerDisconnect(playerID)
		}
	case "player_position":
		if playerPosition, ok := event.GetEventData().(*pb.GameEvent_PlayerPosition); ok {
			// Extraer datos de posición
			playerID := playerPosition.PlayerPosition.PlayerId
			position := playerPosition.PlayerPosition.Position
			
			// Actualizar la posición del jugador en el estado del juego
			s.server.PlayersMutex.RLock()
			player, exists := s.server.Players[playerID]
			s.server.PlayersMutex.RUnlock()
			
			if exists && player.IsActive {
				player.Position = position
				s.server.Logger.LogMessage(
					fmt.Sprintf("Posición actualizada para jugador %d: (%f, %f)", 
						playerID, position.X, position.Y),
				)
				
				// Actualizar el estado del juego
				s.updateGameState()
			}
		}
	}

	// Notificar el evento a todos los clientes
	s.BroadcastEvent(event)

	return &pb.ServerResponse{
		Success:      true,
		ErrorMessage: "",
	}, nil
}

// StreamGame implementa la comunicación bidireccional con los clientes
func (s *GameServiceImpl) StreamGame(stream pb.GameService_StreamGameServer) error {
	// Canal para recibir actualizaciones del cliente
	for {
		// Recibir solicitud del cliente
		req, err := stream.Recv()
		if err != nil {
			s.server.Logger.LogError("Error recibiendo stream", err)
			// Si hay un error en la recepción, asumimos que el cliente se desconectó
			if req != nil {
				s.handlePlayerDisconnect(req.PlayerId)
			}
			return err
		}

		// Procesar la solicitud
		switch r := req.Request.(type) {
		case *pb.ClientRequest_Disconnect:
			s.handlePlayerDisconnect(req.PlayerId)
			return nil
		default:
			s.server.Logger.LogMessage(fmt.Sprintf("Solicitud no manejada: %T", r))
		}

		// Enviar respuesta al cliente con el estado actual
		s.server.StateMutex.RLock()
		gameState := s.server.GameState
		s.server.StateMutex.RUnlock()

		response := &pb.ServerResponse{
			Success: true,
			Response: &pb.ServerResponse_GameState{
				GameState: gameState,
			},
		}

		if err := stream.Send(response); err != nil {
			s.server.Logger.LogError("Error enviando respuesta", err)
			return err
		}
	}
}

// GetGameState implementa el streaming del estado del juego a los clientes
func (s *GameServiceImpl) GetGameState(stream pb.GameService_GetGameStateServer) error {
	// Canal para enviar actualizaciones del estado a los clientes
	for {
		// Recibir solicitud del cliente (heartbeat)
		req, err := stream.Recv()
		if err != nil {
			s.server.Logger.LogError("Error recibiendo solicitud de estado", err)
			return err
		}
		
		// Verificar que sea una solicitud de estado válida
		if req.GetGetGameState() {
			s.server.Logger.LogMessage(
				fmt.Sprintf("Solicitud de estado recibida del jugador %d", req.PlayerId),
			)
			
			// Verificar que el jugador exista
			s.server.PlayersMutex.RLock()
			_, exists := s.server.Players[req.PlayerId]
			s.server.PlayersMutex.RUnlock()
			
			if !exists {
				s.server.Logger.LogMessage(
					fmt.Sprintf("Jugador %d no encontrado al solicitar estado", req.PlayerId),
				)
				return fmt.Errorf("jugador %d no encontrado", req.PlayerId)
			}
			
			// Asegurarse de que el estado del juego esté actualizado
			s.updateGameState()
			
			// Enviar el estado actual del juego
			s.server.StateMutex.RLock()
			gameState := s.server.GameState
			s.server.StateMutex.RUnlock()
			
			s.server.Logger.LogMessage(
				fmt.Sprintf("Enviando estado del juego al jugador %d con %d jugadores activos", 
					req.PlayerId, len(gameState.Players.Players)),
			)
			
			if err := stream.Send(gameState); err != nil {
				s.server.Logger.LogError("Error enviando estado del juego", err)
				return err
			}
		}
	}
}

// Actualiza el estado global del juego
func (s *GameServiceImpl) updateGameState() {
	s.server.StateMutex.Lock()
	defer s.server.StateMutex.Unlock()

	playersList := make([]*pb.PlayerData, 0, len(s.server.Players))
	s.server.PlayersMutex.RLock()
	for _, player := range s.server.Players {
		if player.IsActive {
			playerData := &pb.PlayerData{
				PlayerId:  player.ID,
				Name:      player.Name,
				Position:  player.Position,
				VelocityX: 0,
				Score:     player.Score,
			}
			playersList = append(playersList, playerData)
		}
	}
	s.server.PlayersMutex.RUnlock()

	s.server.GameState = &pb.GameState{
		GameId:    1,
		Players:   &pb.PlayerList{Players: playersList},
		Missiles:  &pb.MissileList{Missiles: []*pb.MissileData{}},
		Meteors:   &pb.MeteorList{Meteors: []*pb.MeteorData{}},
		GameOver:  false,
	}
}

// Maneja la desconexión de un jugador
func (s *GameServiceImpl) handlePlayerDisconnect(playerID int32) {
	s.server.PlayersMutex.Lock()
	var playerName string
	if player, exists := s.server.Players[playerID]; exists {
		playerName = player.Name
		player.IsActive = false
		s.server.Logger.LogMessage(fmt.Sprintf("Jugador desconectado: %s (ID: %d)", player.Name, playerID))
	}
	s.server.PlayersMutex.Unlock()

	// Notificar a todos los clientes conectados sobre la desconexión
	disconnectEvent := &pb.GameEvent{
		EventType: "player_disconnect",
		EventData: &pb.GameEvent_PlayerDisconnect{
			PlayerDisconnect: &pb.PlayerDisconnectEvent{
				PlayerId:   playerID,
				PlayerName: playerName,
			},
		},
	}
	s.BroadcastEvent(disconnectEvent)

	// Actualizar el estado del juego después de la desconexión
	s.updateGameState()
} 