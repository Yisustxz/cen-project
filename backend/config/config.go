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
	file, err := os.Open("../config.json")
	if err != nil {
		return nil, err
	}
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