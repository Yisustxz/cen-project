# Requisitos y configuración para Space Shooter

Este proyecto utiliza Python y la librería Pygame. Se recomienda usar un entorno virtual para aislar las dependencias.

## 1. Crear entorno virtual (usando `venv`)

```bash
python3 -m venv venv
```

## 2. Activar el entorno virtual

- En Linux/Mac:
  ```bash
  source venv/bin/activate
  ```
- En Windows:
  ```cmd
  venv\Scripts\activate
  ```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Ejecutar el juego

```bash
python src/main.py
```

---

## Uso de scripts automáticos

- En Linux/Mac:
  ```bash
  bash setup_linux.sh
  ```
- En Windows:
  ```cmd
  setup_windows.bat
  ```

---

## Estructura del proyecto

```
.
├── images/              # Recursos gráficos
│   ├── meteors/         # Imágenes de meteoritos
│   └── ...
├── src/                 # Código fuente
│   ├── main.py          # Punto de entrada principal
│   └── space_shooter/   # Paquete principal del juego
│       ├── assets/      # Gestión de recursos
│       ├── core/        # Lógica principal
│       ├── entities/    # Entidades del juego
│       ├── ui/          # Componentes de interfaz
│       └── utils/       # Utilidades generales
├── requirements.txt     # Dependencias
├── setup_linux.sh       # Script de configuración para Linux
└── setup_windows.bat    # Script de configuración para Windows
```

## Dependencias

- Python 3.x
- pygame

## Notas

- Asegúrate de tener las imágenes en la carpeta `images/` como en el repositorio.
- Si necesitas instalar pip:
  ```bash
  sudo apt-get install python3-pip
  ```

---

### Para agregar nuevas dependencias

Instala con pip y luego actualiza el archivo `requirements.txt`:

```bash
pip install <paquete>
pip freeze > requirements.txt
```
