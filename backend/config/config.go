package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"os"
	"sync"
)

// MeteorTypeConfig representa la configuración para un tipo de meteorito
type MeteorTypeConfig struct {
	Image              string    `json:"image"`
	SpeedXRange        []float32 `json:"speed_x_range"`
	SpeedYRange        []float32 `json:"speed_y_range"`
	HP                 int       `json:"hp"`
	Points             int       `json:"points"`
	RotationSpeedRange []float32 `json:"rotation_speed_range"`
	HitboxWidth        float32   `json:"hitbox_width"`
	HitboxHeight       float32   `json:"hitbox_height"`
	OffsetX            float32   `json:"offset_x"`
	OffsetY            float32   `json:"offset_y"`
}

// EntityConfig estructura de configuración para entidades
type EntityConfig struct {
	Meteors struct {
		Types      map[string]*MeteorTypeConfig `json:"types"`
		Categories map[string][]string          `json:"categories"`
	} `json:"meteors"`
	Player  map[string]interface{} `json:"player"`
	Missile map[string]interface{} `json:"missile"`
}

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
			Server struct {
				Host string `json:"host"`
				Port int    `json:"port"`
			} `json:"server"`
		} `json:"multiplayerMode"`
		Display struct {
			Width      int  `json:"width"`
			Height     int  `json:"height"`
			Fullscreen bool `json:"fullscreen"`
			FpsLimit   int  `json:"fpsLimit"`
		} `json:"display"`
		Level struct {
			Width  int `json:"width"`
			Height int `json:"height"`
		} `json:"level"`
	} `json:"frontend"`
	Backend struct {
		IP         string  `json:"ip"`
		Port       int     `json:"port"`
		Debug      bool    `json:"debug"`
		MaxPlayers int     `json:"maxPlayers"`
		MaxMeteors int     `json:"maxMeteors"`
		MeteorSpawnFrequency float64 `json:"meteorSpawnFrequency"`
		InitialMeteorCount int     `json:"initialMeteorCount"`
	} `json:"backend"`
}

// GameConfig contiene la configuración del juego y de las entidades
type GameConfig struct {
	Config       *Config
	EntityConfig *EntityConfig
}

// Configuración global
var (
	config       *Config
	entityConfig *EntityConfig
	gameConfig   *GameConfig
	once         sync.Once
	entityOnce   sync.Once
)

// Carga la configuración desde los archivos y la almacena en memoria
func LoadConfig() (*GameConfig, error) {
	once.Do(func() {
		// Cargar la configuración principal
		configPath := "/home/feredev/proyecto-anna/python-space-shooter-main/config.json"
		configFile, err := os.Open(configPath)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[CONFIG MANAGER] Error abriendo config.json: %v\n", err)
			os.Exit(1)
		}
		defer configFile.Close()

		configData, err := ioutil.ReadAll(configFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[CONFIG MANAGER] Error leyendo config.json: %v\n", err)
			os.Exit(1)
		}

		config = &Config{}
		if err := json.Unmarshal(configData, config); err != nil {
			fmt.Fprintf(os.Stderr, "[CONFIG MANAGER] Error parseando config.json: %v\n", err)
			os.Exit(1)
		}

		// Cargar la configuración de entidades
		entityConfigPath := "/home/feredev/proyecto-anna/python-space-shooter-main/entities_config.json"
		entityConfigFile, err := os.Open(entityConfigPath)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[CONFIG MANAGER] Error abriendo entities_config.json: %v\n", err)
			os.Exit(1)
		}
		defer entityConfigFile.Close()

		entityConfigData, err := ioutil.ReadAll(entityConfigFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "[CONFIG MANAGER] Error leyendo entities_config.json: %v\n", err)
			os.Exit(1)
		}

		entityConfig = &EntityConfig{}
		if err := json.Unmarshal(entityConfigData, entityConfig); err != nil {
			fmt.Fprintf(os.Stderr, "[CONFIG MANAGER] Error parseando entities_config.json: %v\n", err)
			os.Exit(1)
		}

		// Crear la configuración completa del juego
		gameConfig = &GameConfig{
			Config:       config,
			EntityConfig: entityConfig,
		}
	})

	if gameConfig == nil {
		fmt.Fprintf(os.Stderr, "[CONFIG MANAGER] No se pudo cargar la configuración\n")
		os.Exit(1)
	}

	return gameConfig, nil
}

// GetServerAddress obtiene la dirección IP y puerto del servidor
func GetServerAddress(cfg *Config) (string, int) {
	if cfg == nil {
		return "localhost", 8080 // Valores por defecto
	}
	return cfg.Backend.IP, cfg.Backend.Port
}

// GetMeteorTypes obtiene todos los tipos de meteoritos disponibles
func GetMeteorTypes(cfg *EntityConfig) []string {
	if cfg == nil || cfg.Meteors.Types == nil {
		return nil
	}

	types := make([]string, 0, len(cfg.Meteors.Types))
	for typeName := range cfg.Meteors.Types {
		types = append(types, typeName)
	}
	return types
}

// Obtiene un tipo aleatorio de meteorito de una categoría específica
func GetMeteorTypeFromCategory(cfg *EntityConfig) string {
	if cfg == nil {
		fmt.Printf("[CONFIG MANAGER] Error: configuración de entidades nula\n")
		os.Exit(1)
	}

	// Verificar que meteors existe
	if cfg.Meteors.Types == nil {
		fmt.Printf("[CONFIG MANAGER] Error: cfg.Meteors.Types es nulo\n")
		os.Exit(1)
	}

	// Verificar que MeteorCategories existe
	if cfg.Meteors.Categories == nil {
		fmt.Printf("[CONFIG MANAGER] Error al obtener categorías de meteoritos: %v\n", cfg)
		os.Exit(1)
	}

	types := GetMeteorTypes(cfg)
	if len(types) == 0 {
		fmt.Printf("[CONFIG MANAGER] No se encontraron tipos de meteoritos\n")
		os.Exit(1)
	}

	return types[rand.Intn(len(types))]
}

// GetMeteorConfig obtiene la configuración para un tipo específico de meteorito
func GetMeteorConfig(cfg *EntityConfig, meteorType string) *MeteorTypeConfig {
	if cfg == nil || cfg.Meteors.Types == nil {
		return nil
	}

	return cfg.Meteors.Types[meteorType]
}

// GetLevelDimensions obtiene las dimensiones del nivel desde la configuración
func GetLevelDimensions(cfg *Config) (int, int) {
	if cfg == nil {
		return 800, 600 // Valores por defecto
	}
	return cfg.Frontend.Level.Width, cfg.Frontend.Level.Height
}

// GetMeteorSpawnFrequency obtiene la frecuencia de generación de meteoritos
func GetMeteorSpawnFrequency() float64 {
	gameConfig, err := LoadConfig()
	if err != nil || gameConfig == nil {
		return 2.0 // Valor por defecto (2 segundos)
	}
	if gameConfig.Config.Backend.MeteorSpawnFrequency > 0 {
		return gameConfig.Config.Backend.MeteorSpawnFrequency
	}
	return 2.0 // Valor por defecto si no está especificado
}

// Obtiene el número máximo de meteoritos permitidos
func GetMaxMeteors() int {
	gameConfig, err := LoadConfig()
	if err != nil || gameConfig == nil {
		// Falla
		fmt.Printf("[CONFIG MANAGER] Error: %v\n", err)
		os.Exit(1)
	}
	if gameConfig.Config.Backend.MaxMeteors > 0 {
		// Loggear el número de meteoritos
		return gameConfig.Config.Backend.MaxMeteors
	}

	// Falla
	fmt.Printf("[CONFIG MANAGER] Error: %v\n", err)
	os.Exit(1)

	return 10 // Valor por defecto si no está especificado
}

// GetMeteorSpawnCount obtiene el número de meteoritos a generar inicialmente
func GetMeteorSpawnCount() int {
	gameConfig, err := LoadConfig()
	if err != nil || gameConfig == nil {
		return 3 // Valor por defecto
	}
	if gameConfig.Config.Backend.InitialMeteorCount > 0 {
		return gameConfig.Config.Backend.InitialMeteorCount
	}
	return 3 // Valor por defecto si no está especificado
}