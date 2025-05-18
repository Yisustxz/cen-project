package entities

import (
	"fmt"
	"math/rand"

	"github.com/Yisustxz/cen-project/backend/config"
	"github.com/Yisustxz/cen-project/backend/engine"
)

// Meteor representa un meteorito en el juego
type Meteor struct {
	engine.BaseGameObject
	MeteorType     string   // Tipo de meteorito (brown_big_1, grey_small_2, etc.)
	Size           float32  // Tamaño del meteorito
	Rotation       float32  // Rotación actual
	RotationSpeed  float32  // Velocidad de rotación
	Health         int      // Puntos de vida
	Points         int      // Puntos que otorga al ser destruido
	DestroyedBy    int32    // ID del jugador que destruyó el meteorito
}

// NewMeteor crea un nuevo meteorito con valores por defecto
func NewMeteor(x, y float32, meteorType string) *Meteor {
	// Valores por defecto
	speedX := float32(rand.Float64()*0.8) - 0.4  // Velocidad en X (-0.4 a 0.4)
	speedY := float32(0.5 + rand.Float64()*1.0)  // Velocidad en Y (0.5 a 1.5)
	rotSpeed := float32(rand.Float64()*0.02 + 0.01) // Velocidad de rotación
	size := float32(32) // Tamaño por defecto, luego se ajusta
	hp := 1  // Puntos de vida por defecto
	points := 10 // Puntos por defecto

	// Ajustar según el tipo
	switch {
	case meteorType == "":
		meteorType = "brown_big_1" // Por defecto
	
	// Tipos grandes
	case meteorType == "brown_big_1", meteorType == "brown_big_2", 
	     meteorType == "grey_big_1", meteorType == "grey_big_2":
		size = 64
		hp = 3
		points = 30
		speedY = float32(0.3 + rand.Float64()*0.5) // Más lento para los grandes
	
	// Tipos medianos
	case meteorType == "brown_medium_1", meteorType == "brown_medium_2", 
	     meteorType == "grey_medium_1", meteorType == "grey_medium_2":
		size = 32
		hp = 2
		points = 20
		speedY = float32(0.4 + rand.Float64()*0.6)
	
	// Tipos pequeños
	case meteorType == "brown_small_1", meteorType == "brown_small_2", 
	     meteorType == "grey_small_1", meteorType == "grey_small_2":
		size = 16
		hp = 1
		points = 10
		speedY = float32(0.6 + rand.Float64()*0.8)
	
	// Tipos diminutos
	case meteorType == "brown_tiny_1", meteorType == "brown_tiny_2", 
	     meteorType == "grey_tiny_1", meteorType == "grey_tiny_2":
		size = 8
		hp = 1 
		points = 5
		speedY = float32(0.7 + rand.Float64()*1.0) // Más rápido para los pequeños
	}

	// Crear meteorito
	m := &Meteor{
		BaseGameObject: engine.BaseGameObject{
			Type: "meteor",
			Position: engine.Vector2D{X: x, Y: y},
			Velocity: engine.Vector2D{X: speedX, Y: speedY},
		},
		MeteorType:    meteorType,
		Size:          size,
		Rotation:      0,
		RotationSpeed: rotSpeed,
		Health:        hp,
		Points:        points,
		DestroyedBy:   -1, // -1 significa que no ha sido destruido
	}

	return m
}

// NewMeteorFromConfig crea un nuevo meteorito utilizando la configuración
func NewMeteorFromConfig(x, y float32, meteorType string, meteorConfig *config.MeteorTypeConfig) *Meteor {
	// Si no se proporciona configuración o es inválida, usar método tradicional
	if meteorConfig == nil {
		return NewMeteor(x, y, meteorType)
	}

	// Obtener valores aleatorios dentro de los rangos de la configuración
	speedX := getRandomValueInRange(meteorConfig.SpeedXRange)
	speedY := getRandomValueInRange(meteorConfig.SpeedYRange)
	rotSpeed := getRandomValueInRange(meteorConfig.RotationSpeedRange)
	
	// Crear meteorito
	m := &Meteor{
		BaseGameObject: engine.BaseGameObject{
			Type: "meteor",
			Position: engine.Vector2D{X: x, Y: y},
			Velocity: engine.Vector2D{X: speedX, Y: speedY},
		},
		MeteorType:    meteorType,
		Size:          meteorConfig.HitboxWidth, // Usamos hitboxWidth como tamaño visual aproximado
		Rotation:      0,
		RotationSpeed: rotSpeed,
		Health:        meteorConfig.HP,
		Points:        meteorConfig.Points,
		DestroyedBy:   -1,
	}

	return m
}

// getRandomValueInRange devuelve un valor aleatorio dentro del rango proporcionado
func getRandomValueInRange(valueRange []float32) float32 {
	// Si el rango no es válido o está vacío, devolver 0
	if valueRange == nil || len(valueRange) < 2 {
		return 0
	}
	
	min := valueRange[0]
	max := valueRange[1]
	
	// Si min y max son iguales, devolver ese valor
	if min == max {
		return min
	}
	
	// Generar un valor aleatorio en el rango [min, max]
	return min + float32(rand.Float64())*(max-min)
}

// Update actualiza el estado del meteorito
func (m *Meteor) Update() {
	// Si ya está destruido, no hacer nada
	if m.DestroyedBy >= 0 {
		return
	}

	// Aplicar un delta time más pequeño para movimiento más lento
	// Usamos 0.016 (16ms) para 60 FPS, lo reducimos más para meteoritos más lentos
	const deltaTime = 0.008 // La mitad de 16ms
	
	// Actualizar posición basada en velocidad y delta time
	m.Position.X += m.Velocity.X * deltaTime
	m.Position.Y += m.Velocity.Y * deltaTime
	
	// Actualizar rotación
	m.Rotation += m.RotationSpeed * deltaTime
	if m.Rotation >= 360 {
		m.Rotation -= 360
	} else if m.Rotation < 0 {
		m.Rotation += 360
	}
}

// TakeDamage reduce los puntos de vida del meteorito y devuelve true si fue destruido
func (m *Meteor) TakeDamage(damage int, playerID int32) bool {
	// Si ya está destruido, no hacer nada
	if m.DestroyedBy >= 0 {
		return true
	}

	m.Health -= damage
	if m.Health <= 0 {
		m.DestroyedBy = playerID
		return true
	}
	return false
}

// IsDestroyed verifica si el meteorito ha sido destruido
func (m *Meteor) IsDestroyed() bool {
	return m.DestroyedBy >= 0
}

// GetDestroyedBy devuelve el ID del jugador que destruyó el meteorito
func (m *Meteor) GetDestroyedBy() int32 {
	return m.DestroyedBy
}

// GetMeteorType devuelve el tipo de meteorito
func (m *Meteor) GetMeteorType() string {
	return m.MeteorType
}

// GetPoints devuelve los puntos que otorga el meteorito
func (m *Meteor) GetPoints() int {
	return m.Points
}

// GetSyncData devuelve los datos para sincronizar el meteorito con los clientes
func (m *Meteor) GetSyncData() map[string]interface{} {
	return map[string]interface{}{
		"id":           m.ID,
		"type":         "meteor",
		"subtype":      m.MeteorType,
		"x":            m.Position.X,
		"y":            m.Position.Y,
		"velocity_x":   m.Velocity.X,
		"velocity_y":   m.Velocity.Y,
		"rotation":     m.Rotation,
		"rot_speed":    m.RotationSpeed,
		"hp":           m.Health,
		"size":         m.Size,
		"destroyed_by": m.DestroyedBy,
	}
}

// String devuelve una representación en texto del meteorito
func (m *Meteor) String() string {
	return fmt.Sprintf("Meteor[ID:%d, Type:%s, Pos:(%.1f,%.1f), Vel:(%.1f,%.1f), HP:%d]", 
		m.ID, m.MeteorType, m.Position.X, m.Position.Y, m.Velocity.X, m.Velocity.Y, m.Health)
}

// GetRandomMeteorType devuelve un tipo de meteorito aleatorio
// Se mantiene por compatibilidad, pero se recomienda usar los métodos del paquete config
func GetRandomMeteorType(category string) string {
	// Tipos por categoría
	meteorTypes := map[string][]string{
		"big": {"brown_big_1", "brown_big_2", "grey_big_1", "grey_big_2"},
		"medium": {"brown_medium_1", "brown_medium_2", "grey_medium_1", "grey_medium_2"},
		"small": {"brown_small_1", "brown_small_2", "grey_small_1", "grey_small_2"},
		"tiny": {"brown_tiny_1", "brown_tiny_2", "grey_tiny_1", "grey_tiny_2"},
		"brown": {"brown_big_1", "brown_big_2", "brown_medium_1", "brown_medium_2", "brown_small_1", "brown_small_2", "brown_tiny_1", "brown_tiny_2"},
		"grey": {"grey_big_1", "grey_big_2", "grey_medium_1", "grey_medium_2", "grey_small_1", "grey_small_2", "grey_tiny_1", "grey_tiny_2"},
	}

	// Si se especificó una categoría y existe, elegir de esa categoría
	if category != "" && len(meteorTypes[category]) > 0 {
		return meteorTypes[category][rand.Intn(len(meteorTypes[category]))]
	}

	// Si no se especificó categoría o no existe, elegir de todos los tipos
	allTypes := []string{
		"brown_big_1", "brown_big_2", "grey_big_1", "grey_big_2",
		"brown_medium_1", "brown_medium_2", "grey_medium_1", "grey_medium_2",
		"brown_small_1", "brown_small_2", "grey_small_1", "grey_small_2",
		"brown_tiny_1", "brown_tiny_2", "grey_tiny_1", "grey_tiny_2",
	}
	return allTypes[rand.Intn(len(allTypes))]
} 