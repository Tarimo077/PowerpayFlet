import flet as ft
from login import login_page
from home import home_page
from deviceList import devices_list_page
from deviceData import device_data_page

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

        if page.route != "/login":

            drawer = ft.NavigationDrawer(
                on_change=handle_navigation,
                controls=[
                    ft.NavigationDrawerDestination(label="HOME", icon=ft.Icons.HOME),
                    ft.NavigationDrawerDestination(label="DEVICES", icon=ft.Icons.DEVELOPER_BOARD),
                    ft.NavigationDrawerDestination(label="LOGOUT", icon=ft.Icons.LOGOUT),
                ],
            )

            menu_icon_btn = ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=lambda e: page.open(drawer),
            )

            app_bar = ft.AppBar(
                title=ft.Text("Powerpay Africa"),
                center_title=True,
                bgcolor=ft.Colors.GREEN,
                leading=menu_icon_btn,
            )

        else:
           
            page.appbar = None
            page.drawer = None

        if page.route == "/":

            # Check if user is logged in (session has "user_id")
            if not page.session.get("user_id"):
                page.go("/login")  # Redirect to login page
                return

            # If logged in, show the home page
            page.views.append(ft.View("/", controls=[home_page(page)], appbar=app_bar, drawer=drawer))

        elif page.route == "/login":
            page.views.append(ft.View("/login", controls=[login_page(page)]))
        elif page.route == "/logout":
            page.session.clear()
            page.go('/login')
        elif page.route == "/devices":
            page.views.append(ft.View("/devices", controls=[devices_list_page(page)],  appbar=app_bar, drawer=drawer))
        elif page.route.startswith("/device/"):
            deviceID = page.route.split("/")[-1]
            print(f"Route: {page.route}")
            app_bar.title = ft.Text(f"{deviceID} data")
            page.views.append(ft.View(f"/device/{deviceID}", controls=[device_data_page(page, deviceID)], appbar=app_bar, drawer=drawer))

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
