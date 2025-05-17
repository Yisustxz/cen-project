"""Motor base para juegos en Pygame."""
import pygame
from pygame.locals import *
import sys
import os

# Añadir el directorio src al path para poder importar
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.objects_manager import ObjectsManager
from space_shooter.utils.delta_time import DeltaTime
import config

class GameEngine:
    """Clase base para manejar la inicialización, bucle y eventos de un juego."""
    
    def __init__(self, width, height, title="Game", fps=60):
        """
        Inicializa el motor del juego.
        
        Args:
            width: Ancho de la ventana
            height: Alto de la ventana
            title: Título de la ventana
            fps: Frames por segundo (valor por defecto, puede ser sobrescrito por la configuración)
        """
        print("Inicializando GameEngine...")
        # Inicializar Pygame
        pygame.init()
        
        # Inicializar el sistema de delta time
        DeltaTime.init()
        
        # Configuración básica
        self.screen_size = (width, height)
        
        # Aplicar configuración de pantalla completa si está habilitada
        display_flags = pygame.FULLSCREEN if config.Config.is_fullscreen() else 0
        self.game_window = pygame.display.set_mode(self.screen_size, display_flags)
        
        pygame.display.set_caption(title)
        
        # Usar el límite de FPS de la configuración, o el valor por defecto si no está disponible
        self.fps = config.Config.get_fps_limit() if hasattr(config.Config, 'get_fps_limit') else fps
        print(f"FPS limitados a: {self.fps}")
        
        # Control del bucle del juego
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
        # Inicializar el gestor de objetos
        self.objects_manager = ObjectsManager(self)
        
        # Modo depuración para mostrar hitboxes
        self.debug_mode = False

        print("GameEngine inicializado correctamente.")
    
    def register_object(self, game_object):
        """
        Registra un objeto para actualización y renderizado automáticos.
        
        Args:
            game_object: Objeto derivado de GameObject
        """
        return self.objects_manager.register(game_object)
    
    def unregister_object(self, game_object):
        """
        Elimina un objeto del registro automático.
        
        Args:
            game_object: Objeto derivado de GameObject
        """
        return self.objects_manager.unregister(game_object)
    
    def register_objects(self, objects_list):
        """
        Registra una lista de objetos para actualización y renderizado automáticos.
        
        Args:
            objects_list: Lista de objetos derivados de GameObject
        """
        self.objects_manager.register_objects(objects_list)
    
    def clear_objects(self):
        """Elimina todos los objetos registrados."""
        self.objects_manager.clear()
    
    def get_objects_by_type(self, obj_type):
        """
        Devuelve la lista de objetos de un tipo específico.
        
        Args:
            obj_type: Tipo de objeto a filtrar
            
        Returns:
            list: Lista de objetos del tipo especificado
        """
        return self.objects_manager.get_objects_by_type(obj_type)
    
    def handle_events(self):
        """
        Maneja los eventos básicos de Pygame.
        Sigue el Principio de Hollywood: maneja primero los eventos base
        y luego llama al método específico de la clase derivada.
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                print("Evento QUIT detectado.")
                self.running = False
            
            # Toggle de depuración con F3
            elif event.type == pygame.KEYDOWN and event.key == K_F3:
                self.debug_mode = not self.debug_mode
                print(f"Modo debug: {'ON' if self.debug_mode else 'OFF'}")
                
                # Si se activa el modo debug, mostrar información sobre los objetos
                if self.debug_mode:
                    self.objects_manager.print_debug_info()
            
            # Permitir que las clases hijas procesen eventos adicionales
            else:
                self.on_handle_event(event)
        
        # Llamar al método específico para manejo de entradas continuas (teclado, mouse, etc.)
        self.on_handle_inputs()
    
    def on_handle_event(self, event):
        """
        Procesa un evento específico.
        Debe ser implementado por clases hijas para manejar eventos discretos.
        
        Args:
            event: Evento de pygame a procesar
        """
        pass
    
    def on_handle_inputs(self):
        """
        Procesa entradas continuas (teclado, mouse, etc).
        Debe ser implementado por clases hijas para manejar entradas continuas.
        """
        pass
    
    def update_objects(self):
        """Actualiza todos los objetos registrados."""
        objects = self.objects_manager.get_objects()
        for obj in list(objects):  # Usamos una copia para permitir modificaciones durante la iteración
            if hasattr(obj, 'update') and callable(obj.update):
                obj.update()
    
    def draw_objects(self):
        """Dibuja todos los objetos registrados."""
        objects = self.objects_manager.get_objects()
        for obj in objects:
            if hasattr(obj, 'draw') and callable(obj.draw):
                obj.draw(self.game_window)
    
    def draw_hitboxes(self):
        """Dibuja hitboxes de todos los objetos registrados en modo depuración."""
        if not self.debug_mode:
            return
            
        objects = self.objects_manager.get_objects()
        for obj in objects:
            if hasattr(obj, 'draw_hitbox') and callable(obj.draw_hitbox):
                obj.draw_hitbox(self.game_window)
    
    def update(self):
        """
        Actualiza la lógica del juego.
        Actualiza primero todos los objetos registrados, detecta colisiones y luego
        llama al método específico de la clase derivada.
        """
        # Actualizar el sistema de delta time
        DeltaTime.update()
        
        # Actualizar todos los objetos registrados
        self.update_objects()
        
        # Detectar colisiones entre objetos
        self.objects_manager.detect_collisions()
        
        # Permitir que las clases hijas realicen actualizaciones adicionales
        self.on_update()
    
    def on_update(self):
        """
        Método para actualizaciones específicas del juego.
        Debe ser implementado por clases hijas.
        """
        pass
    
    def render(self):
        """
        Renderiza el juego.
        Gestiona el renderizado base y luego llama al renderizado específico.
        """
        # Limpiar la pantalla (color negro por defecto)
        self.game_window.fill((0, 0, 0))
        
        # Permitir que las clases hijas realicen renderizado específico de fondo
        self.on_render_background()
        
        # Dibujar todos los objetos registrados
        self.draw_objects()
        
        # Dibujar hitboxes si está activado el modo depuración (encima de los sprites para mayor visibilidad)
        self.draw_hitboxes()
        
        # Permitir que las clases hijas realicen renderizado específico adicional
        self.on_render_foreground()
        
        # Mostrar FPS en modo debug
        if self.debug_mode:
            font = pygame.font.Font(None, 24)
            current_fps = int(self.clock.get_fps())
            fps_text = f"FPS: {current_fps}/{self.fps} | Delta: {DeltaTime.get_delta():.4f}"
            fps_color = (255, 255, 255) if current_fps <= self.fps else (255, 100, 100)  # Rojo si excede el límite
            fps_surface = font.render(fps_text, True, fps_color)
            self.game_window.blit(fps_surface, (10, 10))
        
        # Actualizar la pantalla
        pygame.display.update()
    
    def on_render_background(self):
        """
        Renderiza elementos específicos del juego en el fondo.
        Debe ser implementado por clases hijas.
        """
        pass
    
    def on_render_foreground(self):
        """
        Renderiza elementos específicos del juego en el primer plano.
        Debe ser implementado por clases hijas.
        """
        pass
    
    def run(self):
        """Inicia el bucle principal del juego."""
        print("Iniciando bucle del juego...")
        
        # Inicializar recursos específicos del juego
        self.init_game()
        
        # Bucle principal del juego
        try:
            while self.running:
                # Manejar eventos
                self.handle_events()
                
                # Si no está pausado, actualizar la lógica
                if not self.paused:
                    self.update()
                
                # Renderizar
                self.render()
                
                # Controlar FPS
                self.clock.tick(self.fps)
        
        except Exception as e:
            print(f"Error en el bucle principal: {e}")
            import traceback
            traceback.print_exc()
        
        # Limpieza final
        self.cleanup()
        pygame.quit()
    
    def init_game(self):
        """
        Inicializa recursos específicos del juego.
        Debe ser implementado por clases hijas.
        """
        pass
    
    def cleanup(self):
        """
        Limpia recursos antes de cerrar.
        Debe ser implementado por clases hijas.
        """
        pass
    
    def toggle_pause(self):
        """Alterna el estado de pausa del juego."""
        self.paused = not self.paused
        print(f"Juego {'pausado' if self.paused else 'reanudado'}")
    
    def quit(self):
        """Detiene el bucle del juego."""
        print("Saliendo del juego...")
        self.running = False
    
    def emit_event(self, event_type, data=None, target_type=None):
        """
        Emite un evento a todos los objetos registrados o solo a un tipo específico.
        
        Args:
            event_type: Tipo de evento a emitir
            data: Datos asociados al evento (opcional)
            target_type: Tipo de objeto destinatario (opcional, si es None se envía a todos)
            
        Returns:
            bool: True si el evento fue emitido, False en caso contrario
        """
        try:
            # Comprobar si existe un método específico para este evento
            handler_method = f"on_{event_type}"
            if hasattr(self, handler_method) and callable(getattr(self, handler_method)):
                getattr(self, handler_method)(data)
                
            # Obtener objetos destinatarios
            if target_type:
                objects = self.objects_manager.get_objects_by_type(target_type)
            else:
                objects = self.objects_manager.get_objects()
                
            # Enviar el evento a cada objeto
            for obj in objects:
                if hasattr(obj, 'on_game_event'):
                    obj.on_game_event(event_type, data)
                    
            return True
        except Exception as e:
            print(f"Error al emitir evento {event_type}: {e}")
            return False
    
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
        return self.objects_manager.get_nearest_object(x, y, obj_type, max_distance)
    
    def count_objects_by_type(self, obj_type):
        """
        Cuenta el número de objetos de un tipo específico.
        
        Args:
            obj_type: Tipo de objeto a contar
            
        Returns:
            int: Número de objetos del tipo especificado
        """
        return self.objects_manager.count_objects_by_type(obj_type)
    
    def filter_objects(self, filter_func):
        """
        Filtra objetos según una función personalizada.
        
        Args:
            filter_func: Función que recibe un objeto y devuelve True/False
            
        Returns:
            list: Lista de objetos que cumplen el criterio
        """
        return self.objects_manager.filter_objects(filter_func) 