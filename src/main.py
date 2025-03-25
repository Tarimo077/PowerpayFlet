import flet as ft
from login import login_page
from home import home_page
from deviceList import devices_list_page
from deviceData import device_data_page
from firebase_config import fetch_user_data
from user_profile import user_profile_page


def main(page: ft.Page):
    """Main function to render the Flet UI.."""
    page.title = "Powerpay Africa"



    def handle_navigation(e):
        selected = e.control.selected_index
        if selected == 0:
            page.go("/")
        elif selected ==1:
            page.go("/devices")
        elif selected == 2:
            page.go("/logout")

    def route_change(e: ft.RouteChangeEvent):
        """Handles route changes dynamically."""

        page.views.clear()
        def insert_img():
            profile_img = ft.Container(
                content=ft.Image(
                    src=page.session.get("profile_url"),
                    fit=ft.ImageFit.COVER  # Ensures the image fills the container
                ),
                width=50,  # Adjust size as needed
                height=50,  # Adjust size as needed
                border_radius=ft.border_radius.all(80),  # Half of width/height to make it round
                clip_behavior=ft.ClipBehavior.HARD_EDGE,  # Ensures image stays within bounds
                alignment=ft.alignment.center,
                margin=ft.margin.only(right=10, bottom=5)
            )

            app_bar.actions = [profile_img]
        

        if page.route != "/login":

            drawer = ft.NavigationDrawer(
                on_change=handle_navigation,
                controls=[
                    ft.Container(content=ft.Text("PowerPay Africa", size=24, text_align=ft.TextAlign.CENTER), padding=ft.padding.only(bottom=30, top=10)),
                    #ft.Divider(color=ft.Colors.WHITE, thickness=2),
                    ft.NavigationDrawerDestination(label="HOME", icon=ft.Icons.HOME),
                    ft.NavigationDrawerDestination(label="DEVICES", icon=ft.Icons.DEVELOPER_BOARD),
                    ft.NavigationDrawerDestination(label="LOGOUT", icon=ft.Icons.LOGOUT),
                    ft.Divider(color=ft.Colors.WHITE, thickness=3),
                    ft.Container(content=ft.Row(
                        [
                            ft.Container(
                                        content=ft.Image(
                                            src=page.session.get("profile_url"),
                                            fit=ft.ImageFit.COVER  # Ensures the image fills the container
                                        ),
                                        width=50,  # Adjust size as needed
                                        height=50,  # Adjust size as needed
                                        border_radius=ft.border_radius.all(80),  # Half of width/height to make it round
                                        clip_behavior=ft.ClipBehavior.HARD_EDGE,  # Ensures image stays within bounds
                                        alignment=ft.alignment.center,
                                        margin=ft.margin.only(right=10, bottom=5)
                                    ),
                            ft.TextButton("Edit Profile", icon=ft.Icons.EDIT_ROUNDED, icon_color=ft.Colors.WHITE,
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE, alignment=ft.alignment.center), on_click=page.go("/profile_page"))
                                ]))
                    #ft.Container(content=ft.Row([ft.Icon(name=ft.Icons.COPYRIGHT_ROUNDED, color=ft.Colors.WHITE), ft.Text(" 2025 Powerpay Africa. All Rights Reserved")]), alignment=ft.alignment.bottom_center, expand=True)
                ],
            )
            
            menu_icon_btn = ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=lambda e: page.open(drawer),
                icon_color=ft.Colors.WHITE
            )

            app_bar = ft.AppBar(
                title=ft.Text("Powerpay Africa", color=ft.Colors.WHITE),
                center_title=True,
                bgcolor=ft.Colors.GREEN,
                leading=menu_icon_btn

            )

        else:
           
            page.appbar = None
            page.drawer = None

        if page.route == "/":
            # Check if user is logged in (session has "user_id")
            if not page.session.get("user_id"):
                page.go("/login")  # Redirect to login page
                return

            insert_img()
            # If logged in, show the home page
            page.views.append(ft.View("/", controls=[home_page(page)], appbar=app_bar, drawer=drawer))

        elif page.route == "/login":
            page.views.append(ft.View("/login", controls=[login_page(page)]))
        elif page.route == "/logout":
            page.session.clear()
            page.go('/login')
        elif page.route == "/devices":
            # Check if user is logged in (session has "user_id")
            if not page.session.get("user_id"):
                page.go("/login")  # Redirect to login page
                return
            insert_img()
            page.views.append(ft.View("/devices", controls=[devices_list_page(page)],  appbar=app_bar, drawer=drawer))
        elif page.route.startswith("/device/"):
            # Check if user is logged in (session has "user_id")
            if not page.session.get("user_id"):
                page.go("/login")  # Redirect to login page
                return
            insert_img()
            deviceID = page.route.split("/")[-1]
            app_bar.title = ft.Text(f"{deviceID} data", color=ft.Colors.WHITE)
            page.views.append(ft.View(f"/device/{deviceID}", controls=[device_data_page(page, deviceID)], appbar=app_bar, drawer=drawer))
        elif page.route == "/profile_page":
            # Check if user is logged in (session has "user_id")
            if not page.session.get("user_id"):
                page.go("/login")  # Redirect to login page
                return
            page.views.append(ft.View("/profile_page", controls=[user_profile_page(page)], appbar=app_bar, drawer=drawer))

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if not page.route:
        page.route = "/login"

    page.go(page.route)

ft.app(main, assets_dir="assets")
