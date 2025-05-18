package core

import (
	"fmt"
	"time"

	"github.com/Yisustxz/cen-project/backend/engine"
	"github.com/Yisustxz/cen-project/backend/internal/service"
	"github.com/Yisustxz/cen-project/backend/space_shooter/entities"
	"github.com/Yisustxz/cen-project/backend/types"
)

// Game implementa la lógica específica del juego Space Shooter
type Game struct {
	*engine.GameEngine
	gameServer     *types.GameServer
	meteorManager  *MeteorManager  // Gestor de meteoritos
	startTime      time.Time
	serviceImpl    types.GameService // Interfaz para comunicación con clientes
	updateCounter  int
}

// GetMeteorManager devuelve el gestor de meteoritos
func (g *Game) GetMeteorManager() *MeteorManager {
	return g.meteorManager
}

// NewGame crea una nueva instancia del juego
func NewGame(server *types.GameServer, serviceImpl types.GameService) *Game {
	// Crear instancia del juego con el motor base
	game := &Game{
		GameEngine:    engine.NewGameEngine(20), // 20 actualizaciones por segundo
		gameServer:    server,
		startTime:     time.Now(),
		serviceImpl:   serviceImpl,
		updateCounter: 0,
	}
	
	// Inicializar el gestor de meteoritos después de tener el juego completo
	game.meteorManager = NewMeteorManager(game)
	
	// Establecer el Game como manejador de actualizaciones del motor
	game.GameEngine.SetUpdateHandler(game)
	
	// Log de inicialización
	server.Logger.LogMessage("Motor de juego creado con frecuencia de actualización de 20 FPS")
	
	return game
}

// Start inicia el juego
func (g *Game) Start() {
	g.gameServer.Logger.LogMessage("Iniciando game loop del Space Shooter...")
	
	// Iniciar el motor base
	g.GameEngine.Start()
	
	g.gameServer.Logger.LogMessage("Game loop iniciado correctamente!")
}

// Stop detiene el juego
func (g *Game) Stop() {
	// Detener el motor base
	g.GameEngine.Stop()
}

// OnUpdate implementa la interfaz UpdateHandler del motor
// Este método es llamado automáticamente por el motor de juego en cada tick
func (g *Game) OnUpdate() {
	// Incrementar contador
	g.updateCounter++
	
	// Verificar si el ObjectsManager tiene objetos
	objectCount := len(g.ObjectsManager.Objects)
	meteorCount := len(g.GetObjectsByType("meteor"))
	
	// Log periódico (cada 20 actualizaciones para no saturar logs)
	if g.updateCounter%20 == 0 {
		g.gameServer.Logger.LogMessage(
			fmt.Sprintf("Game.OnUpdate: Contador %d - Objetos: %d, Meteoritos: %d", 
				g.updateCounter, objectCount, meteorCount))
	}
	
	// Depuración adicional cada 100 ticks
	if g.updateCounter%100 == 0 {
		g.gameServer.Logger.LogMessage(fmt.Sprintf(
			"[DEBUG] Estado de objetos - ObjectsManager: %v, NextID: %d",
			objectCount, g.ObjectsManager.NextID))
		
		if objectCount > 0 {
			g.gameServer.Logger.LogMessage("[DEBUG] Tipos de objetos registrados:")
			typeCount := make(map[string]int)
			for _, obj := range g.ObjectsManager.Objects {
				typeCount[obj.GetType()]++
			}
			
			for objType, count := range typeCount {
				g.gameServer.Logger.LogMessage(fmt.Sprintf("  - %s: %d", objType, count))
			}
		}
	}
	
	// Actualizar el gestor de meteoritos
	if g.meteorManager != nil {
		g.meteorManager.Update()
	} else if g.updateCounter%50 == 0 {
		g.gameServer.Logger.LogMessage("ALERTA: meteorManager es nil, no se pueden crear nuevos meteoritos")
	}
	
	// Actualizar estado del juego en el servidor
	g.UpdateGameState()
}

// UpdateGameState actualiza el estado del juego en el servidor
func (g *Game) UpdateGameState() {
	if g.gameServer == nil {
		return
	}
	
	// Actualizar el estado del juego en el servidor
	g.gameServer.StateMutex.Lock()
	defer g.gameServer.StateMutex.Unlock()
	
	// Actualizar la lista de meteoritos en el estado del juego
	g.gameServer.GameState.Meteors = g.meteorManager.GetMeteorsProto()
}

// BroadcastMeteorCreated notifica a los clientes de un nuevo meteorito
func (g *Game) BroadcastMeteorCreated(meteor *entities.Meteor) {
	if g.serviceImpl == nil {
		return
	}
	
	// Crear evento para notificar a los clientes
	event := &service.GameEvent{
		EventType: "meteor_created",
		EventData: &service.GameEvent_MeteorCreated{ // Usar el tipo correcto
			MeteorCreated: &service.MeteorCreatedEvent{
				MeteorId:      meteor.GetID(),
				MeteorType:    meteor.GetMeteorType(),
				Position:      meteor.Position.ToProtoVector(),
				Angle:         meteor.Rotation,
				RotationSpeed: meteor.RotationSpeed,
				Velocity:      meteor.Velocity.ToProtoVector(),
			},
		},
	}
	
	// Enviar evento a través del servicio
	g.serviceImpl.BroadcastEvent(event)
}

// BroadcastMeteorDestroyed notifica a los clientes que un meteorito fue destruido
func (g *Game) BroadcastMeteorDestroyed(meteorID int32, playerID int32) {
	if g.serviceImpl == nil {
		return
	}
	
	// Crear evento para notificar a los clientes
	event := &service.GameEvent{
		EventType: "meteor_destroyed",
		EventData: &service.GameEvent_MeteorDestroyed{
			MeteorDestroyed: &service.MeteorDestroyedEvent{
				MeteorId: meteorID,
				PlayerId: playerID,
			},
		},
	}
	
	// Enviar evento a través del servicio
	g.serviceImpl.BroadcastEvent(event)
}

// HandleMissileCollision maneja la colisión de un misil con un meteorito
func (g *Game) HandleMissileCollision(missileID int32, meteorID int32, playerID int32) {
	// Buscar el meteorito
	obj, exists := g.GetObject(meteorID)
	if !exists {
		return
	}
	
	meteor, ok := obj.(*entities.Meteor)
	if !ok {
		return
	}
	
	// Aplicar daño al meteorito
	destroyed := meteor.TakeDamage(1, playerID)
	
	if destroyed {
		// Si el meteorito fue destruido, notificar a los clientes
		g.BroadcastMeteorDestroyed(meteorID, playerID)
		
		// Actualizar puntuación del jugador
		g.UpdatePlayerScore(playerID, 10) // 10 puntos por destruir un meteorito
		
		// Eliminar del motor
		g.UnregisterObject(meteorID)
	}
}

// UpdatePlayerScore actualiza la puntuación de un jugador
func (g *Game) UpdatePlayerScore(playerID int32, points int32) {
	if g.gameServer == nil || g.serviceImpl == nil {
		return
	}
	
	// Actualizar puntuación en el estado del jugador
	g.gameServer.PlayersMutex.Lock()
	player, exists := g.gameServer.Players[playerID]
	if exists {
		// Convertir player.Score a int32 para la suma
		player.Score = int32(player.Score) + points
	}
	g.gameServer.PlayersMutex.Unlock()
	
	// Enviar evento de actualización de puntuación
	event := &service.GameEvent{
		EventType: "score_update",
		EventData: &service.GameEvent_ScoreUpdate{
			ScoreUpdate: &service.ScoreUpdateEvent{
				PlayerId:   playerID,
				ScoreDelta: points,
			},
		},
	}
	
	g.serviceImpl.BroadcastEvent(event)
} 