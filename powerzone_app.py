import flet as ft
import pandas as pd
import os
from datetime import datetime, timedelta

# --- 1. GESTIÓN DE BASE DE DATOS ---
DATA_FILE = "socios_powerzone.csv"

def inicializar_db():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["ID", "Nombre", "Fecha_Vencimiento", "Estado"])
        df.to_csv(DATA_FILE, index=False)

def registrar_en_csv(nombre, dias):
    df = pd.read_csv(DATA_FILE)
    fecha_vence = datetime.now() + timedelta(days=dias)
    nuevo_socio = pd.DataFrame([{
        "ID": len(df) + 1,
        "Nombre": nombre,
        "Fecha_Vencimiento": fecha_vence.strftime("%Y-%m-%d"),
        "Estado": "Activo"
    }])
    df = pd.concat([df, nuevo_socio], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def consultar_estatus(nombre):
    if not os.path.exists(DATA_FILE): return "ERROR", 0
    df = pd.read_csv(DATA_FILE)
    # Buscamos al socio (sin importar mayúsculas/minúsculas)
    socio = df[df["Nombre"].str.lower() == nombre.lower()]
    
    if socio.empty:
        return "NO_EXISTE", 0
    
    fecha_vence = datetime.strptime(socio.iloc[-1]["Fecha_Vencimiento"], "%Y-%m-%d")
    dias_restantes = (fecha_vence - datetime.now()).days + 1
    
    if dias_restantes > 0:
        return "ACTIVO", dias_restantes
    else:
        return "VENCIDO", 0

# --- 2. INTERFAZ DE USUARIO ---
def main(page: ft.Page):
    inicializar_db()
    
    # Configuración estética
    page.title = "POWERZONE PRO"
    page.window_width = 400
    page.window_height = 750
    page.bgcolor = "#111111"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    # Elementos Visuales
    titulo = ft.Text("POWERZONE", size=45, weight="bold", color="#00FFAA")
    subtitulo = ft.Text("FITNESS CLUB", size=16, color="white60")
    
    nombre_tf = ft.TextField(
        label="Nombre del Socio",
        border_color="#00FFAA",
        focused_border_color="#00AAFF",
        prefix_icon=ft.icons.PERSON,
        width=320
    )

    dias_dd = ft.Dropdown(
        label="Seleccionar Plan",
        width=320,
        border_color="#00FFAA",
        options=[
            ft.dropdown.Option("30", "1 Mes"),
            ft.dropdown.Option("90", "Trimestre"),
            ft.dropdown.Option("365", "Anualidad"),
        ]
    )

    # Tarjeta de Respuesta
    resultado_box = ft.Container(
        content=ft.Text("", size=18, weight="bold", text_align="center"),
        padding=20,
        border_radius=12,
        visible=False,
        width=320
    )

    # --- LÓGICA DE BOTONES ---
    def btn_registrar_click(e):
        if nombre_tf.value and dias_dd.value:
            registrar_en_csv(nombre_tf.value, int(dias_dd.value))
            mostrar_alerta("¡SOCIO REGISTRADO!", "#004D40", "#00FFAA")
            nombre_tf.value = ""
            dias_dd.value = None
        else:
            mostrar_alerta("ERROR: DATOS INCOMPLETOS", "#B71C1C", "#FFCDD2")
        page.update()

    def btn_verificar_click(e):
        if not nombre_tf.value:
            mostrar_alerta("ESCRIBE UN NOMBRE", "#424242", "white")
            page.update()
            return
            
        estado, dias = consultar_estatus(nombre_tf.value)
        if estado == "ACTIVO":
            mostrar_alerta(f"ACCESO PERMITIDO\n{dias} días restantes", "#1B5E20", "#CCFF90")
        elif estado == "VENCIDO":
            mostrar_alerta("ACCESO DENEGADO\nMEMBRESÍA VENCIDA", "#B71C1C", "#FFEBEE")
        else:
            mostrar_alerta("SOCIO NO ENCONTRADO", "#E65100", "#FFE0B2")
        page.update()

    def mostrar_alerta(texto, bg, txt_color):
        resultado_box.content.value = texto
        resultado_box.content.color = txt_color
        resultado_box.bgcolor = bg
        resultado_box.visible = True

    # Montaje de la Pantalla
    page.add(
        ft.Column(
            [
                ft.Divider(height=20, color="transparent"),
                ft.Column([titulo, subtitulo], horizontal_alignment="center", spacing=0),
                ft.Divider(height=30, color="transparent"),
                nombre_tf,
                dias_dd,
                ft.Divider(height=10, color="transparent"),
                ft.ElevatedButton(
                    "REGISTRAR SOCIO",
                    icon=ft.icons.ADD_MODERN,
                    bgcolor="#00FFAA",
                    color="black",
                    width=320,
                    height=50,
                    on_click=btn_registrar_click
                ),
                ft.ElevatedButton(
                    "VERIFICAR ACCESO",
                    icon=ft.icons.QR_CODE_SCANNER,
                    bgcolor="#00AAFF",
                    color="white",
                    width=320,
                    height=50,
                    on_click=btn_verificar_click
                ),
                ft.Divider(height=20, color="transparent"),
                resultado_box
            ],
            horizontal_alignment="center"
        )
    )

ft.app(target=main)
