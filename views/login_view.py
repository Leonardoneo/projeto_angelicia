# views/login_view.py
import flet as ft
from database.connection import conectar
from utils.security import verificar_senha

def abrir_tela_login(page: ft.Page, ao_logar_sucesso):
    page.title = "Angelicia - Login de Segurança"
    page.window_width = 400
    page.window_height = 550
    page.window_resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    # Elementos visuais com contraste para fundo lilás
    txt_titulo = ft.Text("Angelicia", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    txt_subtitulo = ft.Text("Sistema de Gestão & Auditoria", size=14, color=ft.Colors.WHITE70)
    
    input_usuario = ft.TextField(
        label="Usuário", 
        width=300, 
        prefix_icon=ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
        border_color=ft.Colors.WHITE,
        focused_border_color="#6F42C1",
        label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        color=ft.Colors.BLACK
    )
    
    input_senha = ft.TextField(
        label="Senha", 
        password=True, 
        can_reveal_password=True, 
        width=300, 
        prefix_icon=ft.Icons.LOCK_OUTLINED,
        border_color=ft.Colors.WHITE,
        focused_border_color="#6F42C1",
        label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        color=ft.Colors.BLACK
    )
    
    txt_erro = ft.Text("", color=ft.Colors.RED_ACCENT, weight=ft.FontWeight.BOLD)

    def realizar_login(e):
        usuario = input_usuario.value.strip()
        senha = input_senha.value.strip()

        if not usuario or not senha:
            txt_erro.value = "Por favor, preencha todos os campos."
            page.update()
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, perfil FROM usuarios WHERE username = ?", (usuario,))
        resultado = cursor.fetchone()
        conn.close()
       
        if resultado:
            hash_salvo, perfil = resultado
            if verificar_senha(senha, hash_salvo):
                txt_erro.value = ""
                print(f"[LOGIN] Sucesso! Logado como {usuario} ({perfil})")
                # ALTERE ESSA LINHA ABAIXO PARA PASSAR O USUÁRIO TAMBÉM:
                ao_logar_sucesso(perfil, usuario)
            else:
                txt_erro.value = "Senha incorreta."
        else:
            txt_erro.value = "Usuário não encontrado."
        
        page.update()

    btn_entrar = ft.ElevatedButton(
        content=ft.Text("Entrar no Sistema", color="#6F42C1", weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.WHITE, 
        width=300, 
        height=45,
        on_click=realizar_login
    )

    # --- CARD DE LOGIN CENTRAL ---
    # Colocamos os campos dentro de um container branco semi-transparente para dar leitura
    card_login = ft.Container(
        content=ft.Column(
            controls=[
                txt_titulo,
                txt_subtitulo,
                ft.Container(height=15),
                input_usuario,
                input_senha,
                txt_erro,
                ft.Container(height=10),
                btn_entrar
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        bgcolor=ft.Colors.WHITE24, # Branco com opacidade de vidro
        padding=30,
        border_radius=15,
        border=ft.Border.all(1, ft.Colors.WHITE30),
        width=360
    )

    # --- CONTAINER MASTER COM GRADIENTE LILÁS NO BACKGROUND ---
    fundo_gradiente = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#D8B4F8", "#A076F9", "#6F42C1"] # Mesma paleta do painel principal
        ),
        content=card_login,
        alignment=ft.Alignment.CENTER,
        expand=True
    )

    page.clean()
    page.add(fundo_gradiente)
    page.update()