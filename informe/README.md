# Informe del Proyecto

Este directorio contiene el informe del proyecto, el cual documenta la implementación de un sistema multijugador para el juego Space Shooter.

## Compilación del informe

El informe está escrito en formato Markdown y puede ser compilado a PDF usando Pandoc.

### Usando el script automatizado

Para facilitar la compilación, se proporcionan scripts que intentarán compilar el informe:

```bash
# Dar permisos de ejecución
chmod +x compilar_pdf.sh

# Ejecutar el script
./compilar_pdf.sh
```

o usando el script Python:

```bash
# Dar permisos de ejecución
chmod +x compilar_pdf.py

# Ejecutar el script
./compilar_pdf.py
```

### Compilación manual con Pandoc

Si prefieres compilar el informe manualmente, puedes usar los siguientes comandos:

```bash
# Compilación directa con pandoc
pandoc -f markdown -o informe.pdf informe.md --toc

# O con opciones adicionales para mejor calidad
pandoc -f markdown -t pdf -o informe.pdf --pdf-engine=xelatex informe.md --toc
```

### Requisitos

Para compilar el informe, necesitarás tener instalado Pandoc:

```bash
# Instalar Pandoc en sistemas basados en Debian/Ubuntu
sudo apt-get install pandoc

# Si deseas usar XeLaTeX como motor PDF (recomendado para mejor calidad)
sudo apt-get install texlive-xetex
```

## Contenido del informe

El informe detalla:

1. Introducción al proyecto
2. Análisis del problema
3. Diseño de la solución
4. Implementación del sistema multijugador
5. Pruebas realizadas
6. Conclusiones
7. Bibliografía

## Características del informe

- **Portada personalizada**: El informe incluye una portada con el logo de la Universidad Católica Andrés Bello.
- **Índice automático**: Se genera un índice de contenidos para facilitar la navegación.
- **Imágenes**: El informe incluye capturas de pantalla del juego ubicadas en la carpeta `images/`.
- **Formato académico**: El informe sigue un formato académico adecuado para la presentación de proyectos universitarios.
