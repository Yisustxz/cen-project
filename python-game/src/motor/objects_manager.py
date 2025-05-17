"""
Gestor de objetos del motor del juego.
"""

class ObjectsManager:
    """
    Clase para gestionar los objetos del juego.
    
    Esta clase gestiona el registro, actualización y colisiones de los objetos del juego.
    """
    
    def __init__(self, game):
        """
        Inicializa el gestor de objetos.
        
        Args:
            game: Referencia al motor del juego
        """
        self.game = game
        self.objects = []
    
    def register_object(self, obj):
        """
        Registra un nuevo objeto en el gestor.
        
        Args:
            obj: Objeto a registrar
            
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        if obj not in self.objects:
            # Vincular el objeto al juego
            if hasattr(obj, 'set_game'):
                obj.set_game(self.game)
                
            # Añadir a la lista principal
            self.objects.append(obj)
            return True
        return False
    
    def unregister_object(self, obj):
        """
        Elimina un objeto del gestor.
        
        Args:
            obj: Objeto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        if obj in self.objects:
            self.objects.remove(obj)
            return True
        return False
    
    def clear_objects(self):
        """Elimina todos los objetos registrados."""
        self.objects.clear()
    
    def get_objects(self):
        """
        Obtiene todos los objetos registrados.
        
        Returns:
            list: Lista de objetos registrados
        """
        return self.objects[:]  # Devolver una copia para evitar modificaciones durante iteración
    
    def get_objects_by_type(self, obj_type):
        """
        Obtiene objetos de un tipo específico.
        
        Args:
            obj_type: Tipo de objeto a filtrar
            
        Returns:
            list: Lista de objetos del tipo especificado
        """
        return [obj for obj in self.objects if hasattr(obj, 'type') and obj.type == obj_type]
    
    def count_objects_by_type(self, obj_type):
        """
        Cuenta objetos de un tipo específico.
        
        Args:
            obj_type: Tipo de objeto a contar
            
        Returns:
            int: Número de objetos del tipo especificado
        """
        return len(self.get_objects_by_type(obj_type))
    
    def update_objects(self):
        """Actualiza todos los objetos registrados."""
        # Usar una copia para evitar errores si se añaden/eliminan objetos durante la actualización
        for obj in self.get_objects():
            if hasattr(obj, 'update') and callable(obj.update):
                obj.update()
    
    def draw_objects(self, surface):
        """
        Dibuja todos los objetos registrados en la superficie proporcionada.
        
        Args:
            surface: Superficie de pygame donde dibujar
        """
        for obj in self.objects:
            if hasattr(obj, 'draw') and callable(obj.draw):
                obj.draw(surface)
    
    def draw_hitboxes(self, surface):
        """
        Dibuja las hitboxes de todos los objetos en modo depuración.
        
        Args:
            surface: Superficie de pygame donde dibujar
        """
        for obj in self.objects:
            if hasattr(obj, 'draw_hitbox') and callable(obj.draw_hitbox):
                obj.draw_hitbox(surface)
    
    def detect_collisions(self):
        """Detecta colisiones entre objetos que tienen hitbox."""
        # Obtener objetos con hitbox
        objects = [obj for obj in self.objects if hasattr(obj, 'has_hitbox') and obj.has_hitbox]
        
        # Comprobar colisiones entre cada par de objetos
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                if obj1.collides_with(obj2):
                    # Notificar colisión a ambos objetos
                    if hasattr(obj1, 'on_collide') and callable(obj1.on_collide):
                        obj1.on_collide(obj2)
                    if hasattr(obj2, 'on_collide') and callable(obj2.on_collide):
                        obj2.on_collide(obj1)
    
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
    
    def filter_objects(self, filter_func):
        """
        Filtra objetos según una función personalizada.
        
        Args:
            filter_func: Función que recibe un objeto y devuelve True/False
            
        Returns:
            list: Lista de objetos que cumplen el criterio
        """
        return [obj for obj in self.objects if filter_func(obj)] 