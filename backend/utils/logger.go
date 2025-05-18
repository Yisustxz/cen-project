package utils

import (
	"fmt"
	"io"
	"log"
	"os"
)

// ConsoleLogger implementa un logger simple que escribe en la consola
type ConsoleLogger struct {
	writer io.Writer
}

// NewConsoleLogger crea un nuevo logger que escribe en la consola
func NewConsoleLogger() *ConsoleLogger {
	return &ConsoleLogger{
		writer: os.Stdout,
	}
}

// LogMessage registra un mensaje en la consola
func (l *ConsoleLogger) LogMessage(message string) {
	log.Println(message)
	fmt.Fprintln(l.writer, message)
}

// LogError registra un error en la consola
func (l *ConsoleLogger) LogError(message string, err error) {
	errorMsg := message
	if err != nil {
		errorMsg += ": " + err.Error()
	}
	
	log.Println(errorMsg)
	fmt.Fprintln(l.writer, errorMsg)
} 