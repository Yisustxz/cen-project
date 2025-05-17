"""
Motor genérico para juegos 2D.

Este módulo proporciona una base para crear juegos 2D con Pygame.
"""
import sys
import os
import pygame

# Importar clases base
from motor.objects_manager import ObjectsManager
from space_shooter.utils.delta_time import DeltaTime
import config

class GameEngine:
    """
    Clase base para implementar juegos 2D.
    
    Esta clase proporciona la funcionalidad principal para crear un juego,
    incluyendo el bucle principal, la gestión de recursos y el manejo de eventos.
    """
    
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
        
        # Configuración del nivel lógico (área de juego)
        self.level_size = (config.Config.get_level_width(), config.Config.get_level_height())
        print(f"Tamaño del nivel lógico: {self.level_size[0]}x{self.level_size[1]}")
        
        # Crear superficie virtual para el nivel
        self.game_surface = pygame.Surface(self.level_size)
        
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
    
    def init_game(self):
        """
        Inicializa las configuraciones específicas del juego.
        Este método debe ser implementado por las clases derivadas.
        """
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas")
    
    def run(self):
        """Ejecuta el bucle principal del juego."""
        print("Iniciando bucle del juego...")
        
        # Inicializar el juego
        self.init_game()
        
        # Bucle principal
        while self.running:
            # Actualizar delta time
            DeltaTime.update()
            
            # Procesar eventos
            self.process_events()
            
            # Manejar entradas continuas
            if not self.paused:
                self.handle_inputs()
            
            # Actualizar lógica del juego
            if not self.paused:
                self.update()
            
            # Renderizar
            self.render()
            
            # Mantener el ritmo del juego
            self.clock.tick(self.fps)
        
        # Limpiar al salir
        self.cleanup()
        
        # Salir de Pygame
        pygame.quit()
        print("Juego finalizado correctamente.")
            
    def process_events(self):
        """Procesa los eventos de Pygame."""
        for event in pygame.event.get():
            # Salir al cerrar la ventana
            if event.type == pygame.QUIT:
                print("Evento QUIT detectado.")
                self.running = False
                
            # Alternar pausa con la tecla P
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused = not self.paused
                print(f"Juego {'pausado' if self.paused else 'reanudado'}")
                
            # Alternar modo debug con F3
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                self.debug_mode = not self.debug_mode
                print(f"Modo debug: {'ON' if self.debug_mode else 'OFF'}")
                
            # Permitir que las clases hijas procesen eventos específicos
            self.on_handle_event(event)
    
    def on_handle_event(self, event):
        """
        Procesa eventos específicos del juego.
        Este método debe ser implementado por las clases derivadas.
        
        Args:
            event: Evento de Pygame a procesar
        """
        pass
    
    def handle_inputs(self):
        """Gestiona las entradas continuas del usuario."""
        # Base: verificar si se presiona ESC para salir
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False
            
        # Permitir que las clases hijas manejen sus propias entradas
        self.on_handle_inputs()
    
    def on_handle_inputs(self):
        """
        Procesa entradas específicas del juego.
        Este método debe ser implementado por las clases derivadas.
        """
        pass
        
    def update(self):
        """Actualiza la lógica del juego."""
        # Actualizar los objetos
        self.objects_manager.update_objects()
        
        # Detectar colisiones
        self.objects_manager.detect_collisions()
        
        # Llamar al método para actualizaciones específicas
        self.on_update()
        
        # Eliminar objetos marcados para destrucción
        self.clean_destroyed_objects()
    
    def on_update(self):
        """
        Actualiza la lógica específica del juego.
        Este método debe ser implementado por las clases derivadas.
        """
        pass
    
    def render(self):
        """
        Renderiza el juego.
        Gestiona el renderizado base y luego llama al renderizado específico.
        """
        # Limpiar la superficie virtual (color negro por defecto)
        self.game_surface.fill((0, 0, 0))
        
        # Dibujar el fondo en la superficie virtual
        self.on_render_background(self.game_surface)
        
        # Dibujar los objetos en la superficie virtual
        self.objects_manager.draw_objects(self.game_surface)
        
        # Dibujar elementos del primer plano en la superficie virtual
        self.on_render_foreground(self.game_surface)
        
        # En modo debug, dibujar las hitboxes en la superficie virtual
        if self.debug_mode:
            self.objects_manager.draw_hitboxes(self.game_surface)
            
            # Mostrar información de depuración sobre FPS
            fps = self.clock.get_fps()
            fps_limit = self.fps
            fps_color = (0, 255, 0) if fps >= fps_limit * 0.95 else (255, 0, 0)
            self.draw_text(self.game_surface, f"FPS: {fps:.1f}/{fps_limit}", (5, 5), fps_color)
            
            # Mostrar tiempo delta usando la clase estática DeltaTime
            dt_text = f"DT: {DeltaTime.get_delta() * 1000:.2f}ms"
            self.draw_text(self.game_surface, dt_text, (5, 25), fps_color)
            
            # Mostrar resolución
            res_text = f"Level: {self.level_size[0]}x{self.level_size[1]} => Window: {self.screen_size[0]}x{self.screen_size[1]}"
            self.draw_text(self.game_surface, res_text, (5, 45), (255, 255, 255))
        
        # Escalar la superficie virtual a la ventana real
        scaled_surface = pygame.transform.scale(self.game_surface, self.screen_size)
        self.game_window.blit(scaled_surface, (0, 0))
        
        # Actualizar la pantalla
        pygame.display.update()
    
    def on_render_background(self, surface):
        """
        Renderiza el fondo específico del juego.
        Este método debe ser implementado por las clases derivadas.
        
        Args:
            surface: Superficie donde dibujar
        """
        pass
    
    def on_render_foreground(self, surface):
        """
        Renderiza elementos en primer plano específicos del juego.
        Este método debe ser implementado por las clases derivadas.
        
        Args:
            surface: Superficie donde dibujar
        """
        pass
    
    def draw_objects(self):
        """Dibuja todos los objetos registrados."""
        # Dibujar objetos en su orden de capa (z_index)
        self.objects_manager.draw_objects(self.game_surface)
    
    def draw_hitboxes(self):
        """Dibuja las hitboxes de todos los objetos en modo depuración."""
        if self.debug_mode:
            self.objects_manager.draw_hitboxes(self.game_surface)
    
    def count_objects_by_type(self, obj_type):
        """
        Cuenta objetos de un tipo específico.
        
        Args:
            obj_type: Tipo de objeto a contar
            
        Returns:
            int: Número de objetos del tipo especificado
        """
        return self.objects_manager.count_objects_by_type(obj_type)
    
    def register_object(self, obj):
        """
        Registra un nuevo objeto en el juego.
        
        Args:
            obj: Objeto a registrar
            
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        return self.objects_manager.register_object(obj)
    
    def unregister_object(self, obj):
        """
        Elimina un objeto del registro del juego.
        
        Args:
            obj: Objeto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        return self.objects_manager.unregister_object(obj)
    
    def clear_objects(self):
        """Elimina todos los objetos registrados."""
        self.objects_manager.clear_objects()
    
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
    
    def quit(self):
        """Sale del juego."""
        self.running = False
    
    def cleanup(self):
        """
        Limpia recursos antes de cerrar.
        Este método debe ser implementado por las clases derivadas.
        """
        print("Limpiando recursos...")
        
        # Limpiar todos los objetos
        self.clear_objects()
        
        print("Recursos limpiados correctamente.")

    def load_resources(self):
        """Carga recursos del juego (imágenes, sonidos, etc)."""
        self.on_load_resources()

    def get_objects_by_type(self, obj_type):
        """
        Obtiene objetos de un tipo específico.
        
        Args:
            obj_type: Tipo de objeto a filtrar
            
        Returns:
            list: Lista de objetos del tipo especificado
        """
        return self.objects_manager.get_objects_by_type(obj_type)

    def create_game_object(self, game_object_class, *args, **kwargs):
        """
        Crea y registra un objeto del juego.
        
        Args:
            game_object_class: Clase del objeto a crear
            *args, **kwargs: Argumentos para el constructor del objeto
            
        Returns:
            object: Instancia creada y registrada
        """
        obj = game_object_class(*args, **kwargs)
        self.objects_manager.register_object(obj)
        return obj

    def draw_text(self, surface, text, position, color=(255, 255, 255), font_size=16):
        """
        Dibuja texto en la superficie.
        
        Args:
            surface: Superficie donde dibujar
            text: Texto a dibujar
            position: Posición (x, y) donde dibujar
            color: Color del texto (r, g, b)
            font_size: Tamaño de la fuente
        """
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(str(text), True, color)
        surface.blit(text_surface, position)
    
    def clean_destroyed_objects(self):
        """Elimina objetos que han sido marcados para destrucción."""
        # Obtener todos los objetos
        all_objects = self.objects_manager.get_objects()
        
        # Filtrar objetos que deben ser destruidos
        for obj in all_objects[:]:  # Usar una copia para iterar
            if hasattr(obj, 'should_destroy') and obj.should_destroy:
                self.unregister_object(obj) 