package entities

import (
	"math/rand"

	"github.com/Yisustxz/cen-project/backend/engine"
)

// Meteor representa un meteorito en el juego
type Meteor struct {
	engine.BaseGameObject
	MeteorType     string
	Size           float32
	Rotation       float32
	RotationSpeed  float32
	Health         int
	Points         int      // Puntos que otorga al ser destruido
	DestroyedBy    int32    // ID del jugador que destruyó el meteorito
}

// MeteorTypes contiene los tipos de meteoritos disponibles
// Estos coinciden con los tipos definidos en el frontend
var MeteorTypes = []string{
	"brown_big_1", "brown_big_2", 
	"brown_medium_1", "brown_medium_2", 
	"brown_small_1", "brown_small_2", 
	"brown_tiny_1", "brown_tiny_2",
	"grey_big_1", "grey_big_2", 
	"grey_medium_1", "grey_medium_2", 
	"grey_small_1", "grey_small_2", 
	"grey_tiny_1", "grey_tiny_2",
}

// Categorías de meteoritos agrupadas por tamaño
var MeteorCategories = map[string][]string{
	"big": {"brown_big_1", "brown_big_2", "grey_big_1", "grey_big_2"},
	"medium": {"brown_medium_1", "brown_medium_2", "grey_medium_1", "grey_medium_2"},
	"small": {"brown_small_1", "brown_small_2", "grey_small_1", "grey_small_2"},
	"tiny": {"brown_tiny_1", "brown_tiny_2", "grey_tiny_1", "grey_tiny_2"},
}

// GetRandomMeteorType devuelve un tipo de meteorito aleatorio, opcionalmente de una categoría específica
func GetRandomMeteorType(category string) string {
	if category != "" {
		if types, ok := MeteorCategories[category]; ok {
			return types[rand.Intn(len(types))]
		}
	}
	return MeteorTypes[rand.Intn(len(MeteorTypes))]
}

// NewMeteor crea un nuevo meteorito
func NewMeteor(x, y float32, meteorType string) *Meteor {
	// Si no se especifica tipo, elegir uno aleatorio
	if meteorType == "" {
		meteorType = GetRandomMeteorType("")
	}
	
	m := &Meteor{
		BaseGameObject: engine.BaseGameObject{
			Type: "meteor",
			Position: engine.Vector2D{X: x, Y: y},
		},
		MeteorType:    meteorType,
		Rotation:      rand.Float32() * 360,
		DestroyedBy:   -1, // -1 significa que no ha sido destruido
	}
	
	// Factor de reducción de velocidad para hacer más lento el movimiento
	const velocityReductionFactor = 1
	
	// Configurar según tipo - basado en entities_config.json
	if isBigMeteor(meteorType) {
		m.Size = 48
		m.Health = 3
		m.Points = 100
		m.RotationSpeed = (rand.Float32() * 240) - 120 // Entre -120 y 120
		m.Velocity = engine.Vector2D{
			X: ((rand.Float32() * 120) - 60) * velocityReductionFactor,    // Entre -60 y 60
			Y: (60 + (rand.Float32() * 120)) * velocityReductionFactor,    // Entre 60 y 180
		}
	} else if isMediumMeteor(meteorType) {
		m.Size = 32
		m.Health = 2
		m.Points = 75
		m.RotationSpeed = (rand.Float32() * 240) - 120 // Entre -120 y 120
		m.Velocity = engine.Vector2D{
			X: ((rand.Float32() * 180) - 90) * velocityReductionFactor,    // Entre -90 y 90
			Y: (120 + (rand.Float32() * 120)) * velocityReductionFactor,   // Entre 120 y 240
		}
	} else if isSmallMeteor(meteorType) {
		m.Size = 20
		m.Health = 1
		m.Points = 50
		m.RotationSpeed = (rand.Float32() * 300) - 150 // Entre -150 y 150
		m.Velocity = engine.Vector2D{
			X: ((rand.Float32() * 240) - 120) * velocityReductionFactor,   // Entre -120 y 120
			Y: (120 + (rand.Float32() * 180)) * velocityReductionFactor,   // Entre 120 y 300
		}
	} else { // tiny meteor
		m.Size = 14
		m.Health = 1
		m.Points = 25
		m.RotationSpeed = (rand.Float32() * 360) - 180 // Entre -180 y 180
		m.Velocity = engine.Vector2D{
			X: ((rand.Float32() * 300) - 150) * velocityReductionFactor,   // Entre -150 y 150
			Y: (180 + (rand.Float32() * 180)) * velocityReductionFactor,   // Entre 180 y 360
		}
	}
	
	// Aplicar velocidad adicional para meteoritos grises (más veloces)
	if isGreyMeteor(meteorType) {
		m.Health += 1  // Los grises tienen 1 punto más de vida
		m.Points += 20 // Dan más puntos
	}
	
	return m
}

// Helper functions para identificar categorías de meteoritos
func isBigMeteor(meteorType string) bool {
	for _, t := range MeteorCategories["big"] {
		if t == meteorType {
			return true
		}
	}
	return false
}

func isMediumMeteor(meteorType string) bool {
	for _, t := range MeteorCategories["medium"] {
		if t == meteorType {
			return true
		}
	}
	return false
}

func isSmallMeteor(meteorType string) bool {
	for _, t := range MeteorCategories["small"] {
		if t == meteorType {
			return true
		}
	}
	return false
}

func isGreyMeteor(meteorType string) bool {
	return len(meteorType) >= 4 && meteorType[:4] == "grey"
}

// Update actualiza el meteorito
func (m *Meteor) Update() {
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

// TakeDamage reduce la salud del meteorito
func (m *Meteor) TakeDamage(damage int, playerID int32) bool {
	m.Health -= damage
	if m.Health <= 0 {
		m.DestroyedBy = playerID
		return true // Meteorito destruido
	}
	return false // Meteorito sigue vivo
}

// IsDestroyed verifica si el meteorito ha sido destruido
func (m *Meteor) IsDestroyed() bool {
	return m.Health <= 0
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