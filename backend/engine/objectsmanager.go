package engine

import (
	"fmt"
	"sync"
)

// ObjectsManager gestiona todas las entidades del juego
type ObjectsManager struct {
	Objects     map[int32]GameObject
	NextID      int32
	Mutex       sync.RWMutex
}

// NewObjectsManager crea una nueva instancia del gestor de objetos
func NewObjectsManager() *ObjectsManager {
	return &ObjectsManager{
		Objects: make(map[int32]GameObject),
		NextID:  0,
	}
}

// RegisterObject registra un nuevo objeto
func (om *ObjectsManager) RegisterObject(obj GameObject) int32 {
	om.Mutex.Lock()
	defer om.Mutex.Unlock()
	
	om.NextID++
	obj.SetID(om.NextID)
	om.Objects[om.NextID] = obj
	
	return om.NextID
}

// UnregisterObject elimina un objeto por su ID
func (om *ObjectsManager) UnregisterObject(id int32) {
	om.Mutex.Lock()
	defer om.Mutex.Unlock()
	
	delete(om.Objects, id)
}

// GetObject obtiene un objeto por su ID
func (om *ObjectsManager) GetObject(id int32) (GameObject, bool) {
	om.Mutex.RLock()
	defer om.Mutex.RUnlock()
	
	obj, exists := om.Objects[id]
	return obj, exists
}

// UpdateObjects actualiza todos los objetos
func (om *ObjectsManager) UpdateObjects() {
	om.Mutex.RLock()
	
	// Crear una copia de las claves para evitar problemas al modificar el mapa durante la iteración
	var keys []int32
	for k := range om.Objects {
		keys = append(keys, k)
	}
	
	// Verificar si hay objetos antes de actualizar
	objectCount := len(keys)
	if objectCount == 0 {
		om.Mutex.RUnlock()
		return
	}
	
	om.Mutex.RUnlock()
	
	// Actualizar cada objeto
	for _, id := range keys {
		om.Mutex.RLock()
		obj, exists := om.Objects[id]
		om.Mutex.RUnlock()
		
		if exists {
			// Guardar tipo y posición para depuración
			objType := obj.GetType()
			
			// Llamar a Update
			obj.Update()
			
			// Verificar si aún existe después de actualizar (depuración)
			om.Mutex.RLock()
			_, stillExists := om.Objects[id]
			om.Mutex.RUnlock()
			
			if !stillExists {
				// Objeto eliminado durante la actualización, podría ser un error
				println(fmt.Sprintf("ALERTA: Objeto ID %d tipo %s eliminado durante Update", id, objType))
			}
		}
	}
	
	// Verificar recuento final de objetos
	om.Mutex.RLock()
	finalCount := len(om.Objects)
	om.Mutex.RUnlock()
	
	if finalCount != objectCount {
		println(fmt.Sprintf("ALERTA: Recuento de objetos cambió durante UpdateObjects: antes=%d, después=%d", 
			objectCount, finalCount))
	}
}

// GetObjectsByType obtiene todos los objetos de un tipo específico
func (om *ObjectsManager) GetObjectsByType(objType string) []GameObject {
	om.Mutex.RLock()
	defer om.Mutex.RUnlock()
	
	var result []GameObject
	for _, obj := range om.Objects {
		if obj.GetType() == objType {
			result = append(result, obj)
		}
	}
	return result
}

// Clear elimina todos los objetos
func (om *ObjectsManager) Clear() {
	om.Mutex.Lock()
	defer om.Mutex.Unlock()
	
	om.Objects = make(map[int32]GameObject)
} 