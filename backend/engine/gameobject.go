package engine

import (
	"github.com/Yisustxz/cen-project/backend/internal/service"
)

// GameObject es la interfaz base para todas las entidades
type GameObject interface {
	GetID() int32
	SetID(id int32)
	GetType() string
	Update()
	OnCollide(other GameObject) bool
}

// Vector2D representa un vector 2D en el juego
type Vector2D struct {
	X float32
	Y float32
}

// ToProtoVector convierte un Vector2D en un service.Vector2D para protobuf
func (v *Vector2D) ToProtoVector() *service.Vector2D {
	return &service.Vector2D{
		X: v.X,
		Y: v.Y,
	}
}

// FromProtoVector convierte un service.Vector2D en un Vector2D
func FromProtoVector(v *service.Vector2D) Vector2D {
	return Vector2D{
		X: v.X,
		Y: v.Y,
	}
}

// BaseGameObject implementa la funcionalidad común
type BaseGameObject struct {
	ID       int32
	Type     string
	Position Vector2D
	Velocity Vector2D
}

// GetID devuelve el ID del objeto
func (g *BaseGameObject) GetID() int32 {
	return g.ID
}

// SetID establece el ID del objeto
func (g *BaseGameObject) SetID(id int32) {
	g.ID = id
}

// GetType devuelve el tipo del objeto
func (g *BaseGameObject) GetType() string {
	return g.Type
}

// Update actualiza el objeto (método básico que actualiza la posición)
func (g *BaseGameObject) Update() {
	// Actualizar posición basada en velocidad
	g.Position.X += g.Velocity.X
	g.Position.Y += g.Velocity.Y
}

// OnCollide maneja la colisión con otro objeto (implementación base que no hace nada)
func (g *BaseGameObject) OnCollide(other GameObject) bool {
	return false
} 