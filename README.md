# simulador-posicionamiento-aereo
Simulador de tráfico y posicionamiento aéreo en tiempo real desarrollado con Python, Tkinter, hilos y procesamiento de imágenes.
# ✈️ Air Positioning Simulator | Control System

Simulador de escritorio avanzado desarrollado en **Python** con **Tkinter**, diseñado para el control de rutas de vuelo automáticas y manuales sobre un mapa interactivo con telemetría en tiempo real y radar dinámico.

## 🚀 Características Principales
* **Modo Automático:** Simulación de trayectorias aéreas internacionales (Ecuador, Colombia, Perú, Brasil, USA, España, Japón) con cálculo dinámico de distancias en millas, tiempos y velocidad en MPH.
* **Modo Manual:** Control interactivo de la aeronave mediante teclado (`W`, `A`, `S`, `D`) y funcionalidad de arrastre (*Drag & Drop*) con el mouse.
* **Radar Dinámico:** Animación de escaneo de radar en tiempo real integrada en el panel de control.
* **Hilos (Threading):** Uso de concurrencia para evitar bloqueos en la interfaz gráfica durante los cálculos de vuelo.
* **Gestión de Recursos Gráficos:** Carga dinámica y redimensionamiento de mapas e iconos vectoriales mediante `Pillow (PIL)`.

## 🛠️ Tecnologías y Librerías
* **Lenguaje:** Python 3.x
* **Interfaz Gráfica:** `tkinter`
* **Procesamiento de Imágenes:** `Pillow` (`Image`, `ImageTk`)
* **Concurrencia:** `threading`
* **Utilidades del Sistema:** `math`, `time`, `os`

## ⚙️ Estructura del Proyecto
```text
├── simulador.py       # Script principal de la aplicación
├── imagen.png         # Mapa mundi estilizado de fondo
└── avion.png          # Icono real de la aeronave
