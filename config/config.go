package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
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
	// Lista de posibles ubicaciones para el archivo de configuración
	possiblePaths := []string{
		"config.json",                              // En el directorio actual
		"../config.json",                           // En el directorio padre
		"../../config.json",                        // En el directorio abuelo
		filepath.Join("..", "..", "config.json"),   // Alternativa más segura para el directorio abuelo
	}

	var file *os.File
	var err error
	var usedPath string

	// Intentar abrir el archivo en cada ubicación posible
	for _, path := range possiblePaths {
		file, err = os.Open(path)
		if err == nil {
			usedPath = path
			break
		}
	}

	if err != nil {
		return nil, fmt.Errorf("no se pudo encontrar el archivo config.json en ninguna ubicación: %v", err)
	}
	
	fmt.Printf("Usando archivo de configuración en: %s\n", usedPath)
	defer file.Close()

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