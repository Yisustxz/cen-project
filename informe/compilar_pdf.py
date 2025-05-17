#!/usr/bin/env python3
"""
Script para convertir el archivo informe.tex a formato PDF.
Este script intenta varias opciones disponibles en el sistema.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_color(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def print_success(text):
    print_color(text, "32")

def print_error(text):
    print_color(text, "31")

def print_info(text):
    print_color(text, "36")

def print_warning(text):
    print_color(text, "33")

def check_file_exists(file_path):
    if not os.path.exists(file_path):
        print_error(f"¡Error! Archivo no encontrado: {file_path}")
        return False
    return True

def check_command_exists(command):
    return shutil.which(command) is not None

def compile_with_pdflatex():
    """Intenta compilar con pdflatex."""
    print("Intentando compilar con pdflatex...")
    try:
        subprocess.run(["pdflatex", "informe.tex"], check=True)
        subprocess.run(["pdflatex", "informe.tex"], check=True)  # Segunda pasada para TOC
        
        # Limpiar archivos temporales
        for ext in [".aux", ".log", ".out", ".toc"]:
            if os.path.exists(f"informe{ext}"):
                os.remove(f"informe{ext}")
        
        print("¡Compilación con pdflatex exitosa!")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error al compilar con pdflatex.")
        return False

def compile_with_pandoc():
    print_info("Intentando compilar con Pandoc...")
    
    if not check_command_exists("pandoc"):
        print_error("Pandoc no está instalado.")
        print_info("Puedes instalarlo con: sudo apt install pandoc")
        return False
    
    try:
        result = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "pdf", "-o", "informe.pdf", "--pdf-engine=xelatex", "informe.md", "--toc"],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        print_success("¡Documento compilado exitosamente con Pandoc (xelatex)!")
        print_info(f"PDF generado: {os.path.abspath('informe.pdf')}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error al compilar con Pandoc (xelatex): {e}")
        print_error(f"Detalles del error:\n{e.stderr}")
        
        # Intentar con opciones alternativas
        print_warning("Intentando con opciones alternativas...")
        try:
            result = subprocess.run(
                ["pandoc", "-f", "markdown", "-o", "informe.pdf", "informe.md", "--toc"],
                check=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )
            print_success("¡Documento compilado exitosamente con Pandoc (motor por defecto)!")
            print_info(f"PDF generado: {os.path.abspath('informe.pdf')}")
            return True
        except subprocess.CalledProcessError as e2:
            print_error(f"Error al compilar con opciones alternativas: {e2}")
            return False

def compile_with_latexjs():
    """Intenta compilar con latex-js."""
    print("Intentando compilar con latex-js...")
    try:
        subprocess.run(["latex-js", "informe.tex", "-o", "informe.pdf"], check=True)
        print("¡Compilación con latex-js exitosa!")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error al compilar con latex-js.")
        return False

def install_pdflatex():
    """Sugiere cómo instalar pdflatex."""
    print("\nPara instalar pdflatex en Ubuntu, ejecuta:")
    print("  sudo apt update")
    print("  sudo apt install texlive-latex-base texlive-latex-recommended texlive-fonts-recommended texlive-lang-spanish")

def install_pandoc():
    """Sugiere cómo instalar pandoc."""
    print("\nPara instalar pandoc en Ubuntu, ejecuta:")
    print("  sudo apt update")
    print("  sudo apt install pandoc")

def install_latexjs():
    """Sugiere cómo instalar latex-js."""
    print("\nPara instalar latex-js en Ubuntu, ejecuta:")
    print("  sudo apt update")
    print("  sudo apt install nodejs npm")
    print("  sudo npm install -g latex-js")

def suggest_online_services():
    """Sugiere servicios en línea para compilar LaTeX."""
    print("\nAlternativamente, puedes usar servicios en línea:")
    print("1. Overleaf: https://www.overleaf.com/")
    print("2. LaTeX Base: https://latexbase.com/")
    print("3. LaTeX.Online: https://latexonline.cc/")

def main():
    print_info("=== Compilador de informe ===")
    
    # Comprobar si el archivo existe
    if not check_file_exists("informe.md"):
        print_error("No se encontró el archivo informe.md")
        print_info(f"Directorio actual: {os.getcwd()}")
        return 1
    
    # Intentar compilar con Pandoc
    if compile_with_pandoc():
        return 0
    
    print_error("¡No se pudo compilar el documento con ninguno de los métodos disponibles!")
    print_info("Sugerencias:")
    print_info("  1. Asegúrate de tener pandoc instalado: sudo apt install pandoc")
    print_info("  2. Para mejor compatibilidad, instala texlive-xetex: sudo apt install texlive-xetex")
    print_info("  3. Revisa el archivo Markdown en busca de errores de sintaxis")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
