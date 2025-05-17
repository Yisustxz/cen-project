"""Gestor de objetos para el motor de juego."""

class ObjectsManager:
    """
    Gestiona el registro y mantenimiento de los objetos del juego.
    Permite clasificar objetos por tipo y obtener referencias a ellos.
    """
    
    def __init__(self, game=None):
        """
        Inicializa el gestor de objetos.
        
        Args:
            game: Referencia opcional al juego principal
        """
        # Lista principal de todos los objetos registrados
        self.objects = []
        
        # Diccionario para acceder a objetos por tipo
        self.objects_by_type = {}
        
        # Referencia al juego principal (opcional)
        self.game = game
    
    def register(self, game_object):
        """
        Registra un objeto para actualización y renderizado automáticos.
        
        Args:
            game_object: Objeto derivado de GameObject
            
        Returns:
            bool: True si el objeto fue registrado, False si ya estaba registrado
        """
        if game_object not in self.objects:
            # Agregar a la lista principal
            self.objects.append(game_object)
            
            # Clasificar por tipo si está disponible
            if hasattr(game_object, 'type'):
                obj_type = game_object.type
                if obj_type not in self.objects_by_type:
                    self.objects_by_type[obj_type] = []
                self.objects_by_type[obj_type].append(game_object)
            
            # Inyectar referencia al juego si está disponible
            if self.game and hasattr(game_object, 'set_game'):
                game_object.set_game(self.game)
                
            return True
        return False
    
    def unregister(self, game_object):
        """
        Elimina un objeto del registro automático.
        
        Args:
            game_object: Objeto derivado de GameObject
            
        Returns:
            bool: True si el objeto fue eliminado, False si no estaba registrado
        """
        if game_object in self.objects:
            # Eliminar de la lista principal
            self.objects.remove(game_object)
            
            # Eliminar de la clasificación por tipo
            if hasattr(game_object, 'type') and game_object.type in self.objects_by_type:
                if game_object in self.objects_by_type[game_object.type]:
                    self.objects_by_type[game_object.type].remove(game_object)
                
                # Eliminar la lista si está vacía
                if not self.objects_by_type[game_object.type]:
                    del self.objects_by_type[game_object.type]
            
            return True
        return False
    
    def register_objects(self, objects_list):
        """
        Registra una lista de objetos.
        
        Args:
            objects_list: Lista de objetos derivados de GameObject
        """
        for obj in objects_list:
            self.register(obj)
    
    def clear(self):
        """Elimina todos los objetos registrados."""
        self.objects.clear()
        self.objects_by_type.clear()
    
    def get_objects(self):
        """Devuelve la lista completa de objetos registrados."""
        return self.objects
    
    def get_objects_by_type(self, obj_type):
        """
        Devuelve la lista de objetos de un tipo específico.
        
        Args:
            obj_type: Tipo de objeto a filtrar
            
        Returns:
            list: Lista de objetos del tipo especificado
        """
        return self.objects_by_type.get(obj_type, [])
    
    def set_game(self, game):
        """
        Establece la referencia al juego principal.
        
        Args:
            game: Referencia al juego principal
        """
        self.game = game
        
        # Actualizar la referencia en los objetos existentes
        for obj in self.objects:
            if hasattr(obj, 'set_game'):
                obj.set_game(game)
    
    def print_debug_info(self):
        """Imprime información de depuración sobre los objetos registrados."""
        print("\n=== INFORMACIÓN DE OBJETOS ===")
        print(f"Objetos registrados: {len(self.objects)}")
        
        # Contar tipos de objetos por clase
        class_types = {}
        for obj in self.objects:
            obj_class = obj.__class__.__name__
            if obj_class in class_types:
                class_types[obj_class] += 1
            else:
                class_types[obj_class] = 1
        
        # Imprimir conteo por clase
        print("Tipos de objetos por clase:")
        for obj_class, count in class_types.items():
            print(f"  - {obj_class}: {count}")
        
        # Imprimir conteo por tipo personalizado
        if self.objects_by_type:
            print("\nTipos de objetos personalizados:")
            for obj_type, objs in self.objects_by_type.items():
                print(f"  - {obj_type}: {len(objs)}")
        
        # Imprimir información de hitboxes
        print("\nEstado de hitboxes:")
        for obj in self.objects:
            if hasattr(obj, 'has_hitbox'):
                hitbox_status = "Activa" if obj.has_hitbox else "Inactiva"
                hitbox_size = getattr(obj, 'hitbox', None)
                if hitbox_size:
                    print(f"  - {obj.__class__.__name__}: {hitbox_status}, Tamaño: {hitbox_size.width}x{hitbox_size.height}")
                else:
                    print(f"  - {obj.__class__.__name__}: {hitbox_status}")
        
        print("==============================\n")
    
    def detect_collisions(self):
        """
        Detecta colisiones entre todos los objetos registrados y llama a sus métodos on_collide.
        Este método debe ser llamado durante la actualización del juego.
        """
        # Obtener una copia de los objetos para evitar problemas si se modifica la lista durante el proceso
        objects = list(self.objects)
        
        # Verificar colisiones entre todos los objetos
        for i, obj1 in enumerate(objects):
            # Saltear objetos que no tienen hitbox o no son visibles
            if not hasattr(obj1, 'has_hitbox') or not obj1.has_hitbox or not obj1.is_visible:
                continue
                
            # Comprobar colisiones con otros objetos
            for obj2 in objects[i+1:]:  # Empezar desde i+1 para no comprobar colisiones ya verificadas
                # Saltear objetos que no tienen hitbox o no son visibles
                if not hasattr(obj2, 'has_hitbox') or not obj2.has_hitbox or not obj2.is_visible:
                    continue
                
                # Verificar colisión
                if obj1.collides_with(obj2):
                    # Llamar a los métodos on_collide de ambos objetos si están disponibles
                    collision_handled = False
                    
                    if hasattr(obj1, 'on_collide') and callable(obj1.on_collide):
                        collision_handled |= obj1.on_collide(obj2)
                    
                    if hasattr(obj2, 'on_collide') and callable(obj2.on_collide):
                        collision_handled |= obj2.on_collide(obj1)
                    
                    # Si la colisión fue manejada, podemos interrumpir el bucle para este objeto
                    if collision_handled:
                        break
    
    def emit_event(self, event_type, data=None, target_type=None):
        """
        Emite un evento a todos los objetos registrados o a un tipo específico.
        
        Args:
            event_type: Tipo de evento a emitir
            data: Datos asociados al evento (opcional)
            target_type: Tipo de objeto al que dirigir el evento (opcional)
            
        Returns:
            int: Número de objetos que manejaron el evento
        """
        handled_count = 0
        
        # Determinar los objetos a los que enviar el evento
        if target_type:
            objects = self.get_objects_by_type(target_type)
        else:
            objects = self.objects
        
        # Enviar el evento a cada objeto
        for obj in objects:
            if hasattr(obj, 'on_game_event') and callable(obj.on_game_event):
                if obj.on_game_event(event_type, data):
                    handled_count += 1
        
        return handled_count
    
    def get_nearest_object(self, x, y, obj_type=None, max_distance=None):
        """
        Encuentra el objeto más cercano a una posición dada.
        
        Args:
            x: Coordenada X de referencia
            y: Coordenada Y de referencia
            obj_type: Tipo de objeto a buscar (opcional)
            max_distance: Distancia máxima para considerar (opcional)
            
        Returns:
            object: El objeto más cercano o None si no se encuentra ninguno
        """
        import math
        
        # Determinar los objetos entre los que buscar
        if obj_type:
            objects = self.get_objects_by_type(obj_type)
        else:
            objects = self.objects
        
        nearest = None
        min_distance = float('inf')
        
        for obj in objects:
            if hasattr(obj, 'x') and hasattr(obj, 'y'):
                # Calcular distancia
                distance = math.sqrt((obj.x - x)**2 + (obj.y - y)**2)
                
                # Verificar si es el más cercano hasta ahora
                if distance < min_distance:
                    if max_distance is None or distance <= max_distance:
                        min_distance = distance
                        nearest = obj
        
        return nearest
    
    def count_objects_by_type(self, obj_type):
        """
        Cuenta el número de objetos de un tipo específico.
        
        Args:
            obj_type: Tipo de objeto a contar
            
        Returns:
            int: Número de objetos del tipo especificado
        """
        return len(self.get_objects_by_type(obj_type))
    
    def filter_objects(self, filter_func):
        """
        Filtra objetos según una función personalizada.
        
        Args:
            filter_func: Función que recibe un objeto y devuelve True/False
            
        Returns:
            list: Lista de objetos que cumplen el criterio
        """
        return [obj for obj in self.objects if filter_func(obj)] 