package types

import (
	pb "github.com/Yisustxz/cen-project/backend/internal/service"
)

// GameService define una interfaz para la comunicación entre el servicio y el juego
type GameService interface {
	// BroadcastEvent envía un evento a todos los clientes conectados
	BroadcastEvent(event *pb.GameEvent)
}

// GameServiceForwarder implementa la interfaz GameService y reenvía las llamadas a la implementación real
type GameServiceForwarder struct {
	Impl GameServiceImpl
}

// GameServiceImpl es la interfaz que debe implementar el servicio real
type GameServiceImpl interface {
	BroadcastEvent(event *pb.GameEvent)
}

// BroadcastEvent implementa la interfaz GameService
func (f *GameServiceForwarder) BroadcastEvent(event *pb.GameEvent) {
	f.Impl.BroadcastEvent(event)
} 