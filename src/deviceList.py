import flet as ft
from firebase_config import fetch_user_data

def devices_list_page(page: ft.Page):
    page.title = "Powerpay Africa: Device List"
    page.update()
    progress_ring = ft.Container(ft.ProgressRing(color=ft.Colors.GREEN), alignment=ft.alignment.center, expand=True, visible=False)
    user_uid = page.session.get("user_id")
    doc_dic = fetch_user_data(user_uid)
    devices = doc_dic.get("devices", [])
    def handle_click(e, d):
        progress_ring.visible = True  # or any control you want to show
        page.update()  # force update to reflect the change before navigating
        page.go(f"/device/{d}")
    
    # List container with scrolling
    device_list_view = ft.ListView(
        spacing=10, 
        padding=10, 
        expand=True,  # Allows it to grow inside the container
        auto_scroll=True  # Enables automatic scrolling
    )

    # Populate the list with device items
    for device in devices:
        device_list_view.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(value=device, size=16, text_align=ft.TextAlign.LEFT),
                            expand=True,  # Makes text take available space
                        ),
                        ft.IconButton(
                            icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                            icon_color=ft.Colors.GREEN,
                            highlight_color=ft.Colors.ORANGE,
                            on_click=lambda e, d=device: handle_click(e, d),  # Fix lambda scope issue
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  
                    spacing=10,
                ),
                border=ft.border.all(3, ft.Colors.GREEN),
                border_radius=10,
                margin=10,
                padding=20,
            )
        )

    # Wrapping everything inside a scrollable column
    devices_container = ft.Stack([ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(name=ft.Icons.DEVELOPER_BOARD, color=ft.Colors.GREEN, size=24),
                        ft.Text("Device List", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(device_list_view, expand=True)  # Enables scrolling
            ],
            scroll="auto",  # This makes the entire page scrollable if needed
            expand=True  # Allows the column to fill available space
        ),
        expand=True,  # Ensures scrolling works properly
        padding=ft.padding.only(bottom=30)
    ), progress_ring], expand=True)
    
    return devices_container
