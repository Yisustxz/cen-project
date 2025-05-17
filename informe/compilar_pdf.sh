#!/bin/bash

# Colores para los mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar si el archivo informe.md existe
if [ ! -f "informe.md" ]; then
    echo -e "${RED}Error: No se encontró el archivo informe.md${NC}"
    echo -e "Directorio actual: $(pwd)"
    exit 1
fi

# Comprobar si pandoc está instalado
if command -v pandoc &> /dev/null; then
    echo -e "${BLUE}Pandoc está instalado. Intentando compilar...${NC}"
    
    # Intentar compilar con xelatex como motor
    if pandoc -f markdown -t pdf -o informe.pdf --pdf-engine=xelatex informe.md --toc; then
        echo -e "${GREEN}¡Compilación exitosa con Pandoc (usando XeLaTeX)!${NC}"
        echo -e "${BLUE}PDF generado: $(realpath informe.pdf)${NC}"
        exit 0
    else
        echo -e "${YELLOW}Falló la compilación con XeLaTeX. Intentando método alternativo...${NC}"
        
        # Intentar compilar sin especificar el motor
        if pandoc -f markdown -o informe.pdf informe.md --toc; then
            echo -e "${GREEN}¡Compilación exitosa con Pandoc (motor por defecto)!${NC}"
            echo -e "${BLUE}PDF generado: $(realpath informe.pdf)${NC}"
            exit 0
        fi
    fi
    
    echo -e "${RED}No se pudo compilar el documento con ningún método de Pandoc.${NC}"
else
    echo -e "${RED}Pandoc no está instalado.${NC}"
    echo -e "${BLUE}Puedes instalarlo con: sudo apt install pandoc${NC}"
fi

echo -e "${YELLOW}Sugerencias:${NC}"
echo -e "  1. Asegúrate de tener pandoc instalado: sudo apt install pandoc"
echo -e "  2. Para mejor compatibilidad, instala texlive-xetex: sudo apt install texlive-xetex"
echo -e "  3. Revisa el archivo Markdown en busca de errores de sintaxis"

exit 1 