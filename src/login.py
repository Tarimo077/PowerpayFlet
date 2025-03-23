import flet as ft
from firebase_config import login

def login_page(page: ft.Page):
    """Creates and returns the login page UI."""
    
    page.title = "Login - Powerpay Africa"
    #page.theme_mode = ft.ThemeMode.LIGHT  # ✅ Force light mode
    page.bgcolor = ft.colors.WHITE        # ✅ Set background color to white
    # Powerpay Logo
    powerpay_img = ft.Image(src=f"/pplogo.png", width=200, height=200)

    # Input Fields
    email_input = ft.TextField(label="Email", width=300, prefix_icon=ft.Icons.EMAIL, focused_border_color=ft.Colors.GREEN)
    password_input = ft.TextField(label="Password", password=True, width=300, prefix_icon=ft.Icons.LOCK_ROUNDED, can_reveal_password=True, focused_border_color=ft.Colors.GREEN)
    error_message = ft.Text("", color="red")

    # Login Button
    def handle_login(e):
        error_message.value = ""
        loading_animation = ft.Lottie(src=f"loading.lottie")
        login_button.content.bgcolor = ft.Colors.WHITE
        login_button.content = loading_animation
        page.update()
        email = email_input.value
        password = password_input.value
        user = login(email, password)

        if isinstance(user, dict) and "idToken" in user:
            page.session.set("user_id", user["localId"])
            page.go("/")  # Navigate to dashboard
        else:
            error_message.value = "Invalid email or password"
            login_button.content = ft.ElevatedButton(
                "Login", on_click=handle_login,
                icon=ft.Icons.LOGIN_ROUNDED, 
                color=ft.Colors.WHITE, 
                bgcolor=ft.Colors.GREEN, 
                icon_color=ft.Colors.WHITE)
            page.update()

    login_button = ft.Container(
        content=ft.ElevatedButton(
            "Login", on_click=handle_login,
            icon=ft.Icons.LOGIN_ROUNDED, 
            color=ft.Colors.WHITE, 
            bgcolor=ft.Colors.GREEN, 
            icon_color=ft.Colors.WHITE),
            bgcolor=ft.Colors.WHITE
    )
    # Centered Login Form
    login_form = ft.Container(
        content=ft.Column(
            [
                powerpay_img,
                ft.Text("Login to your account", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                email_input,
                password_input,
                login_button,
                error_message,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center,
        width=page.width,
        padding=10,
        border_radius=10,
        bgcolor=ft.colors.WHITE,  # ✅ Ensure form background is also white
    )

    # ✅ Ensure full-page white background
    return ft.Container(
        content=ft.Column(
            [login_form],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True  # ✅ Fills the entire page
        ),
        bgcolor=ft.colors.WHITE,  # ✅ Full page white background
        expand=True
    )
