package engine

import (
	"sync"
	"time"
)

// UpdateHandler es una interfaz para objetos que pueden ser actualizados por el motor
type UpdateHandler interface {
	OnUpdate()
}

// GameEngine maneja el bucle principal del juego
type GameEngine struct {
	Running        bool
	ObjectsManager *ObjectsManager
	TickRate       int           // Número de actualizaciones por segundo
	ticker         *time.Ticker
	stopChan       chan struct{} // Canal para señalizar la detención
	mutex          sync.Mutex
	updateHandler  UpdateHandler // Manejador de actualizaciones (patrón Hollywood)
}

// NewGameEngine crea una nueva instancia del motor de juego
func NewGameEngine(tickRate int) *GameEngine {
	if tickRate <= 0 {
		tickRate = 60 // Valor por defecto: 60 actualizaciones por segundo
	}
	
	return &GameEngine{
		ObjectsManager: NewObjectsManager(),
		TickRate:       tickRate,
		stopChan:       make(chan struct{}),
	}
}

// SetUpdateHandler establece el manejador de actualizaciones
func (g *GameEngine) SetUpdateHandler(handler UpdateHandler) {
	g.updateHandler = handler
}

// Start inicia el bucle del juego
func (g *GameEngine) Start() {
	g.mutex.Lock()
	if g.Running {
		g.mutex.Unlock()
		// Ya está ejecutándose
		println("GameEngine.Start: El motor ya está ejecutándose")
		return
	}
	g.Running = true
	g.mutex.Unlock()
	
	println("GameEngine.Start: Iniciando bucle del juego con tick rate", g.TickRate)
	g.ticker = time.NewTicker(time.Second / time.Duration(g.TickRate))
	
	go func() {
		println("GameEngine.Start: Goroutine iniciada")
		tickCount := 0
		for {
			select {
			case <-g.ticker.C:
				tickCount++
				// Mostrar cada 20 ticks para reducir logs
				if tickCount % 20 == 0 {
					println("GameEngine.Start: Tick #", tickCount, "- Objetos activos:", len(g.ObjectsManager.Objects))
				}
				g.Update()
			case <-g.stopChan:
				println("GameEngine.Start: Señal de detención recibida")
				return
			}
		}
	}()
	println("GameEngine.Start: Bucle iniciado correctamente")
}

// Update actualiza todos los objetos del juego
func (g *GameEngine) Update() {
	g.mutex.Lock()
	defer g.mutex.Unlock()
	
	if !g.Running {
		return
	}
	
	// Actualizar todos los objetos
	objectCount := len(g.ObjectsManager.Objects)
	if objectCount > 0 && objectCount % 20 == 0 {
		println("GameEngine.Update: Actualizando", objectCount, "objetos")
	}
	
	// Actualizar objetos del motor
	g.ObjectsManager.UpdateObjects()
	
	// Llamar al manejador de actualizaciones (patrón Hollywood)
	if g.updateHandler != nil {
		g.updateHandler.OnUpdate()
	}
}

// Stop detiene el motor del juego
func (g *GameEngine) Stop() {
	g.mutex.Lock()
	defer g.mutex.Unlock()
	
	if !g.Running {
		return
	}
	
	g.Running = false
	
	if g.ticker != nil {
		g.ticker.Stop()
	}
	
	// Señalizar que se debe detener la goroutine
	close(g.stopChan)
	
	// Reinicializar el canal para futuras ejecuciones
	g.stopChan = make(chan struct{})
}

// RegisterObject registra un nuevo objeto en el gestor de objetos
func (g *GameEngine) RegisterObject(obj GameObject) int32 {
	return g.ObjectsManager.RegisterObject(obj)
}

// UnregisterObject elimina un objeto del gestor de objetos
func (g *GameEngine) UnregisterObject(id int32) {
	g.ObjectsManager.UnregisterObject(id)
}

// GetObject obtiene un objeto por su ID
func (g *GameEngine) GetObject(id int32) (GameObject, bool) {
	return g.ObjectsManager.GetObject(id)
}

// GetObjectsByType obtiene todos los objetos de un tipo específico
func (g *GameEngine) GetObjectsByType(objType string) []GameObject {
	return g.ObjectsManager.GetObjectsByType(objType)
} 