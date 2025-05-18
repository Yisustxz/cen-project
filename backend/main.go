package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/Yisustxz/cen-project/backend/config"
	pb "github.com/Yisustxz/cen-project/backend/internal/service"
	"github.com/Yisustxz/cen-project/backend/server"
	"github.com/Yisustxz/cen-project/backend/types"
	"github.com/Yisustxz/cen-project/backend/utils"
)

func main() {
	// Cargar configuración
	conf, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Error cargando configuración: %v", err)
	}

	// Obtener dirección del servidor
	ip, port := config.GetServerAddress(conf.Config)
	serverAddress := fmt.Sprintf("%s:%d", ip, port)
	// Crear instancia del servidor
	gameServer := &types.GameServer{
		Players:      make(map[int32]*types.Player),
		NextPlayerID: 1,
		GameState: &pb.GameState{
			GameId:   1,
			Players:  &pb.PlayerList{Players: []*pb.PlayerData{}},
			Missiles: &pb.MissileList{Missiles: []*pb.MissileData{}},
			Meteors:  &pb.MeteorList{Meteors: []*pb.MeteorData{}},
			GameOver: false,
		},
	}

	// Configurar el logger
	logger := utils.NewConsoleLogger()
	gameServer.Logger = logger
	gameServer.Output = os.Stdout

	// Crear e iniciar el servicio del juego
	gameService := server.NewGameServiceImpl(gameServer)
	if err := gameService.Start(serverAddress); err != nil {
		logger.LogError("Error al iniciar el servidor", err)
		return
	}

	logger.LogMessage("Servidor Space Shooter iniciado en " + serverAddress)
	logger.LogMessage("Presiona Ctrl+C para detener el servidor")

	// Manejar señales para cierre adecuado
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)

	// Esperar hasta que se reciba una señal de terminación
	<-c
	logger.LogMessage("Servidor detenido")
}
