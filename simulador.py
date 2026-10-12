import tkinter as tk
import math
import time
import threading
import os
from PIL import Image, ImageTk


# ============================================================
#  CONFIGURACIÓN VISUAL
# ============================================================

COLOR_FONDO = "#020617"
COLOR_PANEL = "#0b1220"
COLOR_PANEL2 = "#111827"
COLOR_GRID = "#1e293b"

COLOR_CYAN = "#00f5ff"
COLOR_CYAN_DARK = "#075985"

COLOR_AUTO = "#ff2d55"
COLOR_MANUAL = "#22c55e"

COLOR_AMARILLO = "#facc15"
COLOR_BLANCO = "#ffffff"
COLOR_GRIS = "#94a3b8"


# ============================================================
#  COLORES DE LOS PAÍSES
# ============================================================

COLORES_PAISES = {

    # 🇪🇨 Ecuador
    "Ecuador": "#ffb000",

    # 🇨🇴 Colombia
    "Colombia": "#ffd43b",

    # 🇵🇪 Perú
    "Perú": "#ff5c5c",

    # 🇧🇷 Brasil
    "Brasil": "#39ff88",

    # 🇺🇸 USA
    "USA": "#ff3b3b",

    # 🇪🇸 España
    "España": "#ffffff",

    # 🇯🇵 Japón
    "Japón": "#ffffff"
}


# ============================================================
#  COLORES DE LA RUTA
# ============================================================

# Borde oscuro para dar efecto de brillo
COLOR_RUTA_GLOW = "#92400e"

# Amarillo principal
COLOR_RUTA = "#facc15"

# Centro amarillo muy claro
COLOR_RUTA_CENTRO = "#fff7b2"

# Puntos de navegación
COLOR_PUNTOS_RUTA = "#ffffff"


# ============================================================
# DIMENSIONES
# ============================================================

ANCHO = 1000
ALTO = 500


class SimuladorMapa:

    def __init__(self, root):

        self.root = root

        # ====================================================
        #  VENTANA PRINCIPAL
        # ====================================================

        self.root.title(
            "AIR POSITIONING SIMULATOR | CONTROL SYSTEM"
        )

        self.root.geometry("1100x850")

        self.root.configure(
            bg=COLOR_FONDO
        )

        self.root.resizable(
            False,
            False
        )

        # ====================================================
        #  GESTIÓN DE RECURSOS
        # ====================================================

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        ruta_mapa = os.path.join(
            base_dir,
            "imagen.png"
        )

        ruta_avion = os.path.join(
            base_dir,
            "avion.png"
        )

        # ====================================================
        # CARGAR MAPA
        # ====================================================

        imagen = None

        if os.path.exists(ruta_mapa):

            try:

                imagen = Image.open(
                    ruta_mapa
                ).convert("RGB")

                imagen = imagen.resize(
                    (ANCHO, ALTO)
                )

                print(
                    f"✓ MAPA CARGADO: {ruta_mapa}"
                )

            except Exception as e:

                print(
                    f"⚠ ERROR AL CARGAR imagen.png: {e}"
                )

        if imagen is None:

            imagen = Image.new(
                "RGB",
                (ANCHO, ALTO),
                COLOR_FONDO
            )

            print(
                "⚠ Se utilizará el fondo de respaldo."
            )

        self.bg = ImageTk.PhotoImage(
            imagen
        )

        # ====================================================
        # CARGAR AVIÓN REAL
        # ====================================================

        self.avion_real = None

        if os.path.exists(ruta_avion):

            try:

                avion = Image.open(
                    ruta_avion
                ).convert("RGBA")

                avion.thumbnail(
                    (80, 80)
                )

                self.avion_real = ImageTk.PhotoImage(
                    avion
                )

                print(
                    f"✓ AVIÓN REAL CARGADO: {ruta_avion}"
                )

            except Exception as e:

                print(
                    f"⚠ ERROR AL CARGAR avion.png: {e}"
                )

        else:

            print(
                f"⚠ NO SE ENCONTRÓ: {ruta_avion}"
            )

        # ====================================================
        # CANVAS
        # ====================================================

        self.canvas = tk.Canvas(

            root,

            width=ANCHO,

            height=ALTO,

            bg=COLOR_FONDO,

            highlightthickness=0
        )

        self.canvas.pack(
            pady=(10, 5)
        )

        # ====================================================
        # MAPA
        # ====================================================

        self.canvas.create_image(

            0,
            0,

            anchor="nw",

            image=self.bg
        )

        # ====================================================
        # CUADRÍCULA
        # ====================================================

        self.dibujar_cuadricula()

        # ====================================================
        # PAÍSES
        # ====================================================

        self.paises = {

            "Ecuador": (200, 300),

            "Colombia": (220, 220),

            "Perú": (200, 380),

            "Brasil": (400, 350),

            "USA": (300, 100),

            "España": (650, 180),

            "Japón": (900, 220)
        }

        self.dibujar_paises()

        # ====================================================
        #  POSICIONES
        # ====================================================

        x, y = self.paises["Ecuador"]

        # ====================================================
        # AVIÓN REAL ESTACIONADO
        # ====================================================

        self.avion_estacionado = None

        if self.avion_real is not None:

            self.avion_estacionado = self.canvas.create_image(

                x,
                y,

                image=self.avion_real,

                anchor="center",

                tags="avion_estacionado"
            )

        # ====================================================
        # AVIÓN AUTOMÁTICO
        # ====================================================

        self.avion_auto = self.crear_avion(

            x,
            y,

            COLOR_AUTO
        )

        self.canvas.itemconfigure(

            self.avion_auto,

            state="hidden"
        )

        # ====================================================
        # AVIÓN MANUAL
        # ====================================================

        self.avion_manual = self.crear_avion(

            x + 40,
            y + 40,

            COLOR_MANUAL
        )

        # ====================================================
        # VARIABLES AUTOMÁTICAS
        # ====================================================

        self.dist_total_auto = 0

        self.tiempo_inicio = None

        self.vuelo_activo = False

        # ====================================================
        #  VARIABLES MANUALES
        # ====================================================

        self.dist_total_manual = 0

        self.last_manual_pos = (

            x + 40,
            y + 40
        )

        self.dragging = False

        # ====================================================
        # RADAR
        # ====================================================

        self.radar_angle = 0

        self.animar_radar()

        # ====================================================
        # PANEL INFERIOR
        # ====================================================

        panel = tk.Frame(

            root,

            bg=COLOR_FONDO
        )

        panel.pack(

            fill="x",

            padx=15
        )

        # ====================================================
        #  PANEL AUTOMÁTICO
        # ====================================================

        self.label_auto = tk.Label(

            panel,

            text=
            "✈ AUTOMÁTICO\n"
            "SISTEMA LISTO",

            fg=COLOR_AUTO,

            bg=COLOR_PANEL,

            font=(

                "Consolas",
                10,
                "bold"
            ),

            justify="left",

            anchor="nw",

            width=50,

            height=9,

            padx=15,

            pady=10
        )

        self.label_auto.grid(

            row=0,
            column=0,

            padx=5
        )

        # ====================================================
        #  PANEL MANUAL
        # ====================================================

        self.label_manual = tk.Label(

            panel,

            text=
            "🎮 MANUAL\n"
            "W A S D + MOUSE",

            fg=COLOR_MANUAL,

            bg=COLOR_PANEL,

            font=(

                "Consolas",
                10,
                "bold"
            ),

            justify="left",

            anchor="nw",

            width=50,

            height=9,

            padx=15,

            pady=10
        )

        self.label_manual.grid(

            row=0,
            column=1,

            padx=5
        )

        # ====================================================
        #  CONTROLES
        # ====================================================

        controles = tk.Frame(

            root,

            bg=COLOR_FONDO
        )

        controles.pack(

            pady=10
        )

        # ====================================================
        # BOTÓN INICIO
        # ====================================================

        self.boton_inicio = tk.Button(

            controles,

            text=
            "✈ INICIAR VUELO AUTOMÁTICO",

            command=
            self.iniciar_vuelo,

            bg="#0369a1",

            fg="white",

            activebackground="#0284c7",

            activeforeground="white",

            font=(

                "Arial",
                11,
                "bold"
            ),

            relief="flat",

            padx=20,

            pady=8,

            cursor="hand2"
        )

        self.boton_inicio.grid(

            row=0,
            column=0,

            padx=8
        )

        # ====================================================
        #  BOTÓN RESET
        # ====================================================

        self.boton_reset = tk.Button(

            controles,

            text=
            "↻ REINICIAR",

            command=
            self.reiniciar,

            bg="#334155",

            fg="white",

            activebackground="#475569",

            font=(

                "Arial",
                11,
                "bold"
            ),

            relief="flat",

            padx=20,

            pady=8,

            cursor="hand2"
        )

        self.boton_reset.grid(

            row=0,
            column=1,

            padx=8
        )

        # ====================================================
        #  TECLADO
        # ====================================================

        root.bind(
            "<w>",
            self.mover_manual
        )

        root.bind(
            "<a>",
            self.mover_manual
        )

        root.bind(
            "<s>",
            self.mover_manual
        )

        root.bind(
            "<d>",
            self.mover_manual
        )

        root.bind(
            "<W>",
            self.mover_manual
        )

        root.bind(
            "<A>",
            self.mover_manual
        )

        root.bind(
            "<S>",
            self.mover_manual
        )

        root.bind(
            "<D>",
            self.mover_manual
        )

        # ====================================================
        #  MOUSE
        # ====================================================

        self.canvas.tag_bind(

            self.avion_manual,

            "<ButtonPress-1>",

            self.start_drag
        )

        self.canvas.tag_bind(

            self.avion_manual,

            "<B1-Motion>",

            self.drag
        )

        self.canvas.tag_bind(

            self.avion_manual,

            "<ButtonRelease-1>",

            self.stop_drag
        )

    # ========================================================
    # CREAR AVIÓN
    # ========================================================

    def crear_avion(

        self,
        x,
        y,
        color
    ):

        avion = self.canvas.create_polygon(

            x,
            y - 14,

            x - 7,
            y + 7,

            x - 18,
            y + 15,

            x - 8,
            y + 2,

            x,
            y + 7,

            x + 8,
            y + 2,

            x + 18,
            y + 15,

            x + 7,
            y + 7,

            x,
            y - 14,

            fill=color,

            outline="white",

            width=2
        )

        return avion

    # ========================================================
    # CUADRÍCULA
    # ========================================================

    def dibujar_cuadricula(self):

        for x in range(

            0,
            ANCHO,
            50
        ):

            self.canvas.create_line(

                x,
                0,

                x,
                ALTO,

                fill=COLOR_GRID
            )

        for y in range(

            0,
            ALTO,
            50
        ):

            self.canvas.create_line(

                0,
                y,

                ANCHO,
                y,

                fill=COLOR_GRID
            )

    # ========================================================
    #  PAÍSES CON PINES
    # ========================================================

    def dibujar_paises(self):

        for nombre, (x, y) in self.paises.items():

            color = COLORES_PAISES.get(

                nombre,

                COLOR_BLANCO
            )

            # =================================================
            #  HALO DEL PIN
            # =================================================

            self.canvas.create_oval(

                x - 14,
                y - 14,

                x + 14,
                y + 14,

                fill="",

                outline=color,

                width=2,

                tags=("pais", "pin")
            )

            # =================================================
            # CABEZA DEL PIN
            # =================================================

            self.canvas.create_oval(

                x - 8,
                y - 8,

                x + 8,
                y + 8,

                fill=color,

                outline=COLOR_BLANCO,

                width=2,

                tags=("pais", "pin")
            )

            # =================================================
            #PUNTA DEL PIN
            # =================================================

            self.canvas.create_polygon(

                x - 6,
                y + 3,

                x,
                y + 14,

                x + 6,
                y + 3,

                fill=color,

                outline=COLOR_BLANCO,

                tags=("pais", "pin")
            )

            # =================================================
            #  CENTRO
            # =================================================

            self.canvas.create_oval(

                x - 3,
                y - 3,

                x + 3,
                y + 3,

                fill=COLOR_FONDO,

                outline="",

                tags=("pais", "pin")
            )

            # =================================================
            #  NOMBRE DEL PAÍS
            # =================================================
            self.canvas.create_text(

                x,
                y - 27,

                text=nombre,

                fill=color,

                font=(

                    "Arial",
                    11,
                    "bold"
                ),

                tags=("pais", "nombre_pais")
            )

            # =================================================
            # LÍNEA DECORATIVA
            # =================================================

            self.canvas.create_line(

                x - 22,
                y - 15,

                x + 22,
                y - 15,

                fill=color,

                width=1,

                tags=("pais", "nombre_pais")
            )

    # ========================================================
    # DISTANCIA
    # ========================================================

    def distancia(

        self,
        x1,
        y1,
        x2,
        y2
    ):

        return math.sqrt(

            (x2 - x1) ** 2 +

            (y2 - y1) ** 2

        ) * 0.621

    # ========================================================
    # RADAR
    # ========================================================

    def animar_radar(self):

        self.radar_angle += 5

        if self.radar_angle >= 360:

            self.radar_angle = 0

        self.canvas.delete(
            "radar"
        )

        cx = 920
        cy = 500
        radio = 55

        # =================================================
        # RADAR
        # =================================================

        self.canvas.create_oval(

            cx - radio,
            cy - radio,

            cx + radio,
            cy + radio,

            outline=COLOR_CYAN,

            width=2,

            tags="radar"
        )

        # =================================================
        # BARRIDO
        # =================================================

        rad = math.radians(

            self.radar_angle
        )

        x2 = (

            cx +

            radio *

            math.cos(rad)
        )

        y2 = (

            cy +

            radio *

            math.sin(rad)
        )

        self.canvas.create_line(

            cx,
            cy,

            x2,
            y2,

            fill=COLOR_CYAN,

            width=2,

            tags="radar"
        )

        # =================================================
        # TEXTO
        # =================================================

        self.canvas.create_text(

            cx,
            cy + 70,

            text="RADAR",

            fill=COLOR_CYAN,

            font=(

                "Consolas",
                9,
                "bold"
            ),

            tags="radar"
        )

        self.root.after(

            80,

            self.animar_radar
        )

    # ========================================================
    # INICIAR VUELO
    # ========================================================

    def iniciar_vuelo(self):

        if self.vuelo_activo:

            return

        self.vuelo_activo = True

        self.dist_total_auto = 0

        self.tiempo_inicio = time.time()

        # =================================================
        # Ocultar avión real
        # =================================================

        if self.avion_estacionado is not None:

            self.canvas.itemconfigure(

                self.avion_estacionado,

                state="hidden"
            )

        self.canvas.itemconfigure(

            self.avion_auto,

            state="normal"
        )

        self.boton_inicio.config(

            text=
            "✈ VUELO EN PROGRESO...",

            state="disabled"
        )

        # =================================================
        #  HILO DE VUELO
        # =================================================

        threading.Thread(

            target=self.viajar,

            daemon=True

        ).start()

    # ========================================================
    # VIAJE AUTOMÁTICO
    # ========================================================

    def viajar(self):

        ruta = list(

            self.paises.keys()
        )

        for i in range(

            len(ruta) - 1
        ):

            origen = ruta[i]

            destino = ruta[i + 1]

            x1, y1 = self.paises[

                origen
            ]

            x2, y2 = self.paises[

                destino
            ]

            # =================================================
            #  RUTA AÉREA AMARILLA
            # =================================================

            # Resplandor exterior
            self.canvas.create_line(

                x1,
                y1,

                x2,
                y2,

                fill=COLOR_RUTA_GLOW,

                width=18,

                capstyle="round",

                tags="ruta"
            )

            # Amarillo brillante
            self.canvas.create_line(

                x1,
                y1,

                x2,
                y2,

                fill=COLOR_RUTA,

                width=10,

                capstyle="round",

                tags="ruta"
            )

            # Centro claro
            self.canvas.create_line(

                x1,
                y1,

                x2,
                y2,

                fill=COLOR_RUTA_CENTRO,

                width=2,

                capstyle="round",

                tags="ruta"
            )

            # =================================================
            #  PUNTOS DE TRAYECTORIA
            # =================================================

            for punto in range(

                0,
                101,
                10
            ):

                px = (

                    x1 +

                    (x2 - x1) *

                    punto / 100
                )

                py = (

                    y1 +

                    (y2 - y1) *

                    punto / 100
                )

                self.canvas.create_oval(

                    px - 3,
                    py - 3,

                    px + 3,
                    py + 3,

                    fill=COLOR_PUNTOS_RUTA,

                    outline=COLOR_RUTA,

                    width=1,

                    tags="ruta_puntos"
                )

            # =================================================
            # PINES ARRIBA
            # =================================================

            self.canvas.tag_raise(
                "pais"
            )

            # =================================================
            #  DISTANCIA DEL TRAMO
            # =================================================

            distancia_tramo = self.distancia(

                x1,
                y1,

                x2,
                y2
            )

            # =================================================
            #  MOVIMIENTO DEL AVIÓN
            # =================================================

            for t in range(

                101
            ):

                nx = (

                    x1 +

                    (x2 - x1) *

                    t / 100
                )

                ny = (

                    y1 +

                    (y2 - y1) *

                    t / 100
                )

                # =================================================
                #  ACTUALIZAR AVIÓN
                # =================================================

                self.canvas.coords(

                    self.avion_auto,

                    nx,
                    ny - 14,

                    nx - 7,
                    ny + 7,

                    nx - 18,
                    ny + 15,

                    nx - 8,
                    ny + 2,

                    nx,
                    ny + 7,

                    nx + 8,
                    ny + 2,

                    nx + 18,
                    ny + 15,

                    nx + 7,
                    ny + 7,

                    nx,
                    ny - 14
                )

                # =================================================
                #  PUNTO DE NAVEGACIÓN EN MOVIMIENTO
                # =================================================

                self.canvas.delete(
                    "punto_activo"
                )

                # Halo
                self.canvas.create_oval(

                    nx - 8,
                    ny - 8,

                    nx + 8,
                    ny + 8,

                    fill=COLOR_RUTA_GLOW,

                    outline="",

                    tags="punto_activo"
                )

                # Punto brillante
                self.canvas.create_oval(

                    nx - 4,
                    ny - 4,

                    nx + 4,
                    ny + 4,

                    fill=COLOR_PUNTOS_RUTA,

                    outline=COLOR_RUTA,

                    width=2,

                    tags="punto_activo"
                )

                # =================================================
                #  ESTELA
                # =================================================

                if t % 5 == 0:

                    # Halo de la estela
                    self.canvas.create_oval(

                        nx - 5,
                        ny - 5,

                        nx + 5,
                        ny + 5,

                        fill=COLOR_RUTA_GLOW,

                        outline="",

                        tags="estela"
                    )

                    # Centro
                    self.canvas.create_oval(

                        nx - 2,
                        ny - 2,

                        nx + 2,
                        ny + 2,

                        fill=COLOR_RUTA,

                        outline="",

                        tags="estela"
                    )

                # =================================================
                # MANTENER PINES ARRIBA
                # =================================================

                self.canvas.tag_raise(
                    "pais"
                )

                # Avión arriba de la ruta
                self.canvas.tag_raise(
                    self.avion_auto
                )

                # Punto activo debajo del avión
                self.canvas.tag_raise(
                    "punto_activo"
                )

                # =================================================
                #  TELEMETRÍA
                # =================================================

                distancia_actual = (

                    distancia_tramo *

                    t /

                    100
                )

                self.dist_total_auto += (

                    distancia_tramo / 100
                )

                tiempo = (

                    time.time() -

                    self.tiempo_inicio
                )

                velocidad = 480 + (

                    t % 40
                )

                self.label_auto.config(

                    text=

                    f"✈ AUTOMÁTICO\n\n"

                    f"🛫 {origen}\n"
                    f"   ↓\n"
                    f"🛬 {destino}\n\n"

                    f"📏 TRAMO: "
                    f"{distancia_actual:.2f} mi\n"

                    f"🌍 TOTAL: "
                    f"{self.dist_total_auto:.2f} mi\n"

                    f"⏱ TIEMPO: "
                    f"{tiempo:.2f} s\n"

                    f"⚡ VELOCIDAD: "
                    f"{velocidad} MPH\n\n"

                    f"🟢 ESTADO: EN VUELO"
                )

                time.sleep(
                    0.03
                )

        # ====================================================
        #  VUELO COMPLETADO
        # ====================================================

        self.vuelo_activo = False

        self.canvas.delete(
            "punto_activo"
        )

        self.canvas.itemconfigure(

            self.avion_auto,

            state="normal"
        )

        if self.avion_estacionado is not None:

            self.canvas.itemconfigure(

                self.avion_estacionado,

                state="hidden"
            )

        self.canvas.tag_raise(
            "pais"
        )

        self.canvas.tag_raise(
            self.avion_auto
        )

        # =================================================
        #  PANEL FINAL
        # =================================================

        self.label_auto.config(

            text=

            f"✈ AUTOMÁTICO\n\n"

            f"🏁 VUELO COMPLETADO\n\n"

            f"🌍 DISTANCIA TOTAL:\n"

            f"{self.dist_total_auto:.2f} mi\n\n"

            f"🟢 ESTADO: ATERRIZADO"
        )

        self.boton_inicio.config(

            text=
            "✓ VUELO COMPLETADO"
        )

    # ========================================================
    # MOVIMIENTO MANUAL
    # ========================================================

    def mover_manual(

        self,
        event
    ):

        dx = 0
        dy = 0

        paso = 10

        tecla = event.keysym.lower()

        if tecla == "w":

            dy = -paso

        elif tecla == "s":

            dy = paso

        elif tecla == "a":

            dx = -paso

        elif tecla == "d":

            dx = paso

        self.canvas.move(

            self.avion_manual,

            dx,
            dy
        )

        self.actualizar_manual()

    # ========================================================
    #  INICIO DEL ARRASTRE
    # ========================================================

    def start_drag(

        self,
        event
    ):

        self.dragging = True

    # ========================================================
    #  ARRASTRAR
    # ========================================================

    def drag(

        self,
        event
    ):

        if not self.dragging:

            return

        x = event.x
        y = event.y

        self.canvas.coords(

            self.avion_manual,

            x,
            y - 14,

            x - 7,
            y + 7,

            x - 18,
            y + 15,

            x - 8,
            y + 2,

            x,
            y + 7,

            x + 8,
            y + 2,

            x + 18,
            y + 15,

            x + 7,
            y + 7,

            x,
            y - 14
        )

        self.actualizar_manual()

    # ========================================================
    # TERMINAR ARRASTRE
    # ========================================================

    def stop_drag(

        self,
        event
    ):

        self.dragging = False

    # ========================================================
    # ACTUALIZAR MANUAL
    # ========================================================

    def actualizar_manual(self):

        coords = self.canvas.coords(

            self.avion_manual
        )

        if not coords:

            return

        x = coords[0]

        y = coords[1] + 14

        lx, ly = self.last_manual_pos

        dist = self.distancia(

            lx,
            ly,

            x,
            y
        )

        self.dist_total_manual += dist

        self.last_manual_pos = (

            x,
            y
        )

        self.label_manual.config(

            text=

            f"🎮 MANUAL\n\n"

            f"🎮 CONTROL: ACTIVO\n\n"

            f"📏 MOVIMIENTO:\n"
            f"{dist:.2f} mi\n\n"

            f"🌍 DISTANCIA TOTAL:\n"
            f"{self.dist_total_manual:.2f} mi\n\n"

            f"📍 POSICIÓN:\n"
            f"X = {int(x)}\n"
            f"Y = {int(y)}\n\n"

            f"🟢 ESTADO: CONTROL MANUAL"
        )

    # ========================================================
    #  REINICIAR
    # ========================================================

    def reiniciar(self):

        self.canvas.delete(
            "all"
        )

        # =================================================
        #  MAPA
        # =================================================

        self.canvas.create_image(

            0,
            0,

            anchor="nw",

            image=self.bg
        )

        self.dibujar_cuadricula()

        self.dibujar_paises()

        # =================================================
        #  POSICIÓN INICIAL
        # =================================================

        x, y = self.paises["Ecuador"]

        # =================================================
        #  AVIÓN REAL
        # =================================================

        self.avion_estacionado = None

        if self.avion_real is not None:

            self.avion_estacionado = self.canvas.create_image(

                x,
                y,

                image=self.avion_real,

                anchor="center",

                tags="avion_estacionado"
            )

        # =================================================
        #  AVIÓN AUTOMÁTICO
        # =================================================

        self.avion_auto = self.crear_avion(

            x,
            y,

            COLOR_AUTO
        )

        self.canvas.itemconfigure(

            self.avion_auto,

            state="hidden"
        )

        # =================================================
        # AVIÓN MANUAL
        # =================================================

        self.avion_manual = self.crear_avion(

            x + 40,
            y + 40,

            COLOR_MANUAL
        )

        # =================================================
        #  REINICIAR DATOS
        # =================================================

        self.dist_total_auto = 0

        self.dist_total_manual = 0

        self.last_manual_pos = (

            x + 40,
            y + 40
        )

        self.vuelo_activo = False

        # =================================================
        # RECONECTAR MOUSE
        # =================================================

        self.canvas.tag_bind(

            self.avion_manual,

            "<ButtonPress-1>",

            self.start_drag
        )

        self.canvas.tag_bind(

            self.avion_manual,

            "<B1-Motion>",

            self.drag
        )

        self.canvas.tag_bind(

            self.avion_manual,

            "<ButtonRelease-1>",

            self.stop_drag
        )

        # =================================================
        #  PANEL AUTOMÁTICO
        # =================================================

        self.label_auto.config(

            text=
            "✈ AUTOMÁTICO\n\n"
            "SISTEMA LISTO\n\n"
            "Presiona INICIAR VUELO"
        )

        # =================================================
        #  PANEL MANUAL
        # =================================================

        self.label_manual.config(

            text=
            "🎮 MANUAL\n\n"
            "W → ARRIBA\n"
            "S → ABAJO\n"
            "A → IZQUIERDA\n"
            "D → DERECHA\n\n"
            "🖱 Arrastra el avión"
        )

        # =================================================
        #  BOTÓN
        # =================================================

        self.boton_inicio.config(

            text=
            "✈ INICIAR VUELO AUTOMÁTICO",

            state="normal"
        )


# ============================================================
#  EJECUCIÓN DEL PROGRAMA
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = SimuladorMapa(
        root
    )

    root.mainloop()