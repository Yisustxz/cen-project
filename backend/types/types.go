package types

import (
	"io"
	"os"
	"sync"
	"time"

	pb "github.com/Yisustxz/cen-project/backend/internal/service"
)

// EventStream representa un stream para enviar notificaciones
type EventStream struct {
	Stream      pb.GameService_SubscribeToEventsServer
	LastSeen    time.Time
	Active      bool
}

// Logger interfaz para el registro de mensajes
type Logger interface {
	LogMessage(message string)
	LogError(message string, err error)
}

// Player representa a un jugador conectado
type Player struct {
	ID          int32
	Name        string
	Position    *pb.Vector2D
	Score       int32
	IsActive    bool
	EventStream *EventStream    // Stream para notificaciones
	StreamMutex sync.RWMutex    // Mutex para acceder al stream
}

// GameServer implementa el servicio gRPC
type GameServer struct {
	pb.UnimplementedGameServiceServer
	Players       map[int32]*Player    // Mapa de jugadores por ID
	PlayersMutex  sync.RWMutex         // Mutex para acceder al mapa de jugadores
	NextPlayerID  int32                // ID para el próximo jugador
	GameState     *pb.GameState        // Estado actual del juego
	StateMutex    sync.RWMutex         // Mutex para acceder al estado del juego
	Logger        Logger               // Logger para registrar mensajes
	Output        io.Writer            // Salida para los mensajes de log
}

// Shutdown detiene el servidor de juego por un error crítico
func (s *GameServer) Shutdown() {
	s.Logger.LogMessage("SHUTDOWN: Deteniendo el servidor por un error crítico")
	// Aquí se puede implementar la lógica para detener el servidor
	// Por ahora, solo registramos el mensaje
	os.Exit(1) // Termina el programa con código de error
} 