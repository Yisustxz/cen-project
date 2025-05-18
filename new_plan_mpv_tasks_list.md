# MVP para Multijugador - Lista de Tareas

## Sistema Cliente-Servidor

- [x] Definir arquitectura cliente-servidor simplificada
- [ ] Implementar servidor básico en Go como relay de eventos
- [ ] Crear protocolo de comunicación cliente-servidor

## Cliente (Python)

- [x] Añadir campos de ID a las clases existentes (Player, Missile, Meteor)
- [x] Crear entidades para objetos remotos (OtherPlayer, OtherMissile)
- [ ] Implementar NetworkManager para comunicación con servidor
- [ ] Crear sistema de serialización/deserialización de eventos
- [ ] Modificar Game para registrar objetos remotos

## Eventos de Red

- [ ] Conectar al servidor
- [ ] Registrar jugador
- [ ] Enviar posición de jugador
- [ ] Disparar misil
- [ ] Destruir meteorito
- [ ] Recibir daño
- [ ] Sincronizar puntuación
- [ ] Fin de juego

## Interfaz de Usuario

- [ ] Añadir menú de conexión
- [ ] Mostrar información de jugadores conectados
- [ ] Visualizar puntuaciones de todos los jugadores

## Pruebas

- [ ] Pruebas locales con múltiples instancias
- [ ] Pruebas de latencia y rendimiento
- [ ] Pruebas de reconexión y manejo de errores

## Integración

- [ ] Integrar NetworkManager con sistema de eventos existente
- [ ] Manejar colisiones entre objetos locales y remotos
- [ ] Procesar eventos de red en el bucle principal del juego
