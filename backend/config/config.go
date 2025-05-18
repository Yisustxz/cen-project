package config

import (
	"encoding/json"
	"fmt"
	"os"
)

// Config estructura de configuración del juego
type Config struct {
	Frontend struct {
		SinglePlayerMode struct {
			Enable   bool `json:"enable"`
			SkipMenu bool `json:"skipMenu"`
		} `json:"singlePlayerMode"`
		MultiplayerMode struct {
			Enable   bool   `json:"enable"`
			SkipMenu bool   `json:"skipMenu"`
			IPAddress string `json:"ipAddress"`
			Port     int    `json:"port"`
		} `json:"multiplayerMode"`
	} `json:"frontend"`
	Backend struct {
		IP        string `json:"ip"`
		Port      int    `json:"port"`
		Debug     bool   `json:"debug"`
		MaxPlayers int   `json:"maxPlayers"`
	} `json:"backend"`
}

// LoadConfig carga la configuración desde un archivo JSON
func LoadConfig() (*Config, error) {
	// Intentar diferentes ubicaciones para el archivo config.json
	// Priorizar la raíz del proyecto
	paths := []string{/*"../config.json", */"/home/feredev/proyecto-anna/python-space-shooter-main/config.json"}
	
	var file *os.File
	var err error
	var successPath string
	
	// Probar cada ruta hasta encontrar el archivo
	for _, path := range paths {
		file, err = os.Open(path)
		if err == nil {
			successPath = path
			defer file.Close()
			break
		}
	}
	
	if err != nil {
		return nil, fmt.Errorf("no se pudo encontrar el archivo config.json: %v", err)
	}

	fmt.Printf("Archivo de configuración cargado desde: %s\n", successPath)
	
	config := &Config{}
	decoder := json.NewDecoder(file)
	err = decoder.Decode(config)
	if err != nil {
		return nil, err
	}

	return config, nil
}

// GetServerAddress devuelve la dirección IP y puerto del servidor
func GetServerAddress(config *Config) string {
	return fmt.Sprintf("%s:%d", config.Backend.IP, config.Backend.Port)
} 