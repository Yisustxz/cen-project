package core

import (
	"fmt"
	"math/rand"
	"sync"
	"time"

	"github.com/Yisustxz/cen-project/backend/engine"
	"github.com/Yisustxz/cen-project/backend/internal/service"
	"github.com/Yisustxz/cen-project/backend/space_shooter/entities"
)

// MeteorManager gestiona la creación y eliminación de meteoritos
type MeteorManager struct {
	game            *Game
	spawnFrequency  time.Duration  // Tiempo entre creación de meteoritos
	lastSpawn       time.Time
	levelWidth      float32        // Ancho del nivel
	levelHeight     float32        // Alto del nivel
	maxMeteors      int            // Máximo número de meteoritos en pantalla
	mutex           sync.Mutex
	enabled         bool           // Si está habilitado o no
	meteorCategory  string         // Categoría de meteoritos a generar ("", "big", "medium", "small", "tiny")
	meteorsCreated  int            // Contador de meteoritos creados
}

// GetGame devuelve la referencia al juego
func (mm *MeteorManager) GetGame() *Game {
	return mm.game
}

// NewMeteorManager crea un nuevo gestor de meteoritos
func NewMeteorManager(game *Game) *MeteorManager {
	return &MeteorManager{
		game:           game,
		spawnFrequency: 2 * time.Second,  // Cada 2 segundos por defecto
		lastSpawn:      time.Now().Add(-2 * time.Second), // Para que cree uno inmediatamente
		levelWidth:     800,              // Ancho del nivel
		levelHeight:    600,              // Alto del nivel
		maxMeteors:     2,               // Máximo 10 meteoritos a la vez
		enabled:        true,             // Habilitado por defecto
		meteorCategory: "",               // Todos los tipos
		meteorsCreated: 0,
	}
}

// SetSpawnFrequency establece la frecuencia de generación de meteoritos
func (mm *MeteorManager) SetSpawnFrequency(frequency time.Duration) {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()
	mm.spawnFrequency = frequency
	mm.game.gameServer.Logger.LogMessage(
		fmt.Sprintf("[METEOR MANAGER] Frecuencia de generación cambiada a %v", frequency))
}

// SetLevelDimensions establece las dimensiones del nivel
func (mm *MeteorManager) SetLevelDimensions(width, height float32) {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()
	mm.levelWidth = width
	mm.levelHeight = height
	mm.game.gameServer.Logger.LogMessage(
		fmt.Sprintf("[METEOR MANAGER] Dimensiones del nivel cambiadas a %.0fx%.0f", width, height))
}

// SetMaxMeteors establece el número máximo de meteoritos
func (mm *MeteorManager) SetMaxMeteors(max int) {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()
	mm.maxMeteors = max
	mm.game.gameServer.Logger.LogMessage(
		fmt.Sprintf("[METEOR MANAGER] Máximo de meteoritos cambiado a %d", max))
}

// Enable habilita la generación de meteoritos
func (mm *MeteorManager) Enable() {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()
	mm.enabled = true
	mm.game.gameServer.Logger.LogMessage("[METEOR MANAGER] Generación de meteoritos habilitada")
}

// Disable deshabilita la generación de meteoritos
func (mm *MeteorManager) Disable() {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()
	mm.enabled = false
	mm.game.gameServer.Logger.LogMessage("[METEOR MANAGER] Generación de meteoritos deshabilitada")
}

// SetMeteorCategory establece la categoría de meteoritos a generar
func (mm *MeteorManager) SetMeteorCategory(category string) {
	mm.mutex.Lock()
	defer mm.mutex.Unlock()
	mm.meteorCategory = category
	mm.game.gameServer.Logger.LogMessage(
		fmt.Sprintf("[METEOR MANAGER] Categoría de meteoritos cambiada a '%s'", category))
}

// Update actualiza el gestor de meteoritos
func (mm *MeteorManager) Update() {
	mm.mutex.Lock()
	enabled := mm.enabled
	maxMeteors := mm.maxMeteors
	spawnFrequency := mm.spawnFrequency
	lastSpawn := mm.lastSpawn
	category := mm.meteorCategory
	mm.mutex.Unlock()
	
	// Si está deshabilitado, no hacer nada
	if !enabled {
		return
	}
	
	// Loguear cada 100 actualizaciones (reducido para no saturar)
	if mm.game.updateCounter % 100 == 0 {
		mm.game.gameServer.Logger.LogMessage(
			fmt.Sprintf("[METEOR MANAGER] Estado - Enabled: %v, Frequency: %v",
				enabled, spawnFrequency))
	}
	
	// Verificar si es tiempo de crear un nuevo meteorito
	timeSinceLastSpawn := time.Since(lastSpawn)
	if timeSinceLastSpawn >= spawnFrequency {
		// Contar meteoritos actuales
		meteors := mm.game.GetObjectsByType("meteor")
		meteorCount := len(meteors)
		
		// Si hay menos meteoritos que el máximo, crear uno nuevo
		if meteorCount < maxMeteors {
			// Crear un meteorito - el logging se hace dentro de CreateMeteor
			meteorType := entities.GetRandomMeteorType(category)
			createdMeteor := mm.CreateMeteor(meteorType, nil)
			
			// Incrementar contador si se creó correctamente
			if createdMeteor != nil {
				mm.mutex.Lock()
				mm.meteorsCreated++
				mm.mutex.Unlock()
			}
		} else if mm.game.updateCounter % 20 == 0 {
			mm.game.gameServer.Logger.LogMessage(
				fmt.Sprintf("[METEOR MANAGER] Máximo de meteoritos alcanzado (%d/%d)", 
					meteorCount, maxMeteors))
		}
		
		mm.mutex.Lock()
		mm.lastSpawn = time.Now()
		mm.mutex.Unlock()
	}
	
	// Verificar meteoritos fuera de pantalla
	mm.checkMeteorsOutOfBounds()
}

// checkMeteorsOutOfBounds elimina meteoritos que han salido de la pantalla
func (mm *MeteorManager) checkMeteorsOutOfBounds() {
	meteors := mm.game.GetObjectsByType("meteor")
	levelHeight := mm.levelHeight
	
	meteorRemoved := 0
	
	for _, obj := range meteors {
		meteor, ok := obj.(*entities.Meteor)
		if !ok {
			continue
		}
		
		// Log de posición para depuración
		if mm.game.updateCounter % 20 == 0 {
			mm.game.gameServer.Logger.LogMessage(
				fmt.Sprintf("[METEOR POS] ID: %d, Position: (%.2f, %.2f), Level Height: %.2f", 
				meteor.GetID(), meteor.Position.X, meteor.Position.Y, levelHeight))
		}
		
		// Si el meteorito ha salido por la parte inferior de la pantalla
		if meteor.Position.Y > levelHeight + meteor.Size {
			// Registrar siempre cuando se elimina un meteorito
			mm.game.gameServer.Logger.LogMessage(
				fmt.Sprintf("[METEOR REMOVED] ID: %d, Type: %s, Position: (%.2f, %.2f), Level Height: %.2f", 
				meteor.GetID(), meteor.MeteorType, meteor.Position.X, meteor.Position.Y, levelHeight))
			
			// Eliminar del motor
			mm.game.UnregisterObject(meteor.GetID())
			meteorRemoved++
		}
	}
	
	// Log adicional si se eliminaron meteoritos en esta actualización
	if meteorRemoved > 0 {
		mm.game.gameServer.Logger.LogMessage(
			fmt.Sprintf("[METEOR REMOVAL] Elimiados %d meteoritos en este tick", meteorRemoved))
	}
}

// CreateMeteor crea un nuevo meteorito
func (mm *MeteorManager) CreateMeteor(meteorType string, position *engine.Vector2D) *entities.Meteor {
	mm.mutex.Lock()
	levelWidth := mm.levelWidth
	mm.mutex.Unlock()
	
	// Si no se especifica tipo, elegir uno aleatorio
	if meteorType == "" {
		meteorType = entities.GetRandomMeteorType(mm.meteorCategory)
	}
	
	// Si no se especifica posición, generar una aleatoria
	var x, y float32
	if position != nil {
		x = position.X
		y = position.Y
	} else {
		x = rand.Float32() * levelWidth
		y = -50 // Iniciar fuera de la pantalla, arriba
	}
	
	// Crear meteorito
	meteor := entities.NewMeteor(x, y, meteorType)
	
	// Registrar en el motor del juego
	objID := mm.game.RegisterObject(meteor)
	
	// Asegurarse de que el ID se asignó correctamente
	if objID <= 0 {
		mm.game.gameServer.Logger.LogError("Error registrando meteorito en el motor de juego", nil)
		return nil
	}
	
	// Solo imprimir un log desde aquí para evitar duplicación
	mm.game.gameServer.Logger.LogMessage(
		fmt.Sprintf("[METEOR CREATED] ID: %d, Type: %s, Position: (%.2f, %.2f), Velocity: (%.2f, %.2f)",
		meteor.ID, meteorType, x, y, meteor.Velocity.X, meteor.Velocity.Y))
	
	// Imprimir el estado de los objetos para depuración
	if objID > 0 {
		mm.game.gameServer.Logger.LogMessage(
			fmt.Sprintf("[METEOR DEBUG] Objetos tras registro: %d, Meteoritos: %d", 
			len(mm.game.ObjectsManager.Objects), len(mm.game.GetObjectsByType("meteor"))))
	}
	
	// Notificar a los clientes sobre el nuevo meteorito
	mm.game.BroadcastMeteorCreated(meteor)
	
	return meteor
}

// DestroyMeteor destruye un meteorito y notifica a los clientes
func (mm *MeteorManager) DestroyMeteor(meteorID int32, playerID int32) {
	// Obtener el meteorito
	obj, exists := mm.game.GetObject(meteorID)
	if !exists {
		return
	}
	
	meteor, ok := obj.(*entities.Meteor)
	if !ok {
		return
	}
	
	// Marcar como destruido
	meteor.TakeDamage(meteor.Health, playerID)
	
	// Notificar a los clientes
	mm.game.BroadcastMeteorDestroyed(meteorID, playerID)
	
	// Eliminar del motor
	mm.game.UnregisterObject(meteorID)
	
	mm.game.gameServer.Logger.LogMessage(
		fmt.Sprintf("[METEOR DESTROYED] ID: %d, Type: %s, DestroyedBy: %d, Points: %d",
		meteorID, meteor.MeteorType, playerID, meteor.GetPoints()))
}

// GetMeteorsProto obtiene todos los meteoritos en formato protobuf para enviar a clientes
func (mm *MeteorManager) GetMeteorsProto() *service.MeteorList {
	meteors := mm.game.GetObjectsByType("meteor")
	meteorList := make([]*service.MeteorData, 0, len(meteors))
	
	for _, obj := range meteors {
		m, ok := obj.(*entities.Meteor)
		if !ok {
			continue
		}
		
		meteorData := &service.MeteorData{
			MeteorId:       m.GetID(),
			MeteorType:     m.GetMeteorType(),
			Position:       m.Position.ToProtoVector(),
			Angle:          m.Rotation,
			RotationSpeed:  m.RotationSpeed,
		}
		meteorList = append(meteorList, meteorData)
	}
	
	return &service.MeteorList{
		Meteors: meteorList,
	}
}

// GetRandomMeteorTypeOfCategory obtiene un tipo de meteorito aleatorio de una categoría específica
func (mm *MeteorManager) GetRandomMeteorTypeOfCategory(category string) string {
	return entities.GetRandomMeteorType(category)
} 