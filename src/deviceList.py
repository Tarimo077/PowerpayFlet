import flet as ft
from firebase_config import fetch_user_data


def devices_list_page(page: ft.Page):
    user_uid = page.session.get("user_id")
    print(f"User ID: {user_uid}")
    doc_dic = fetch_user_data(user_uid)
    devices = doc_dic.get("devices", [])
    device_list_view = ft.ListView(spacing=10, padding=10, auto_scroll=True)

    for i in range(0, len(devices)):
        device_list_view.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(value=devices[i], size=16, text_align=ft.TextAlign.LEFT),
                            expand=True,  # Makes text take available space
                        ),
                        ft.IconButton(
                            icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                            icon_color=ft.Colors.GREEN,
                            highlight_color=ft.Colors.ORANGE,
                            on_click=lambda _:page.go(f"/device/{devices[i]}"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Ensures button stays at the right
                    spacing=10,
                ),
                border=ft.border.all(3, ft.Colors.GREEN),
                border_radius=10,
                margin=10,
                padding=20,
            )
        )


    devices_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(name=ft.Icons.DEVELOPER_BOARD, color=ft.Colors.GREEN, size=24),
                ft.Text("Device List", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)                

            ]

            ),
            device_list_view
        ]
            
        )
    )
    return devices_container
    
    