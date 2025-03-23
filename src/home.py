import flet as ft
import requests
from requests.auth import HTTPBasicAuth
from firebase_config import fetch_user_data

# Mapping for dropdown values to minutes
value_map = {
    "All Time": "9999999",
    "5 min": "5",
    "30 min": "30",
    "1 hr": "60",
    "3 hrs": "180",
    "12 hrs": "720",
    "24 hrs": "1440",
    "3 days": "4320",
    "7 days": "10080",
    "2 weeks": "20160",
    "1 month": "40320",
    "3 months": "120960",
    "6 months": "241920",
    "1 year": "483840",
    "3 years": "1451520",
}

# API Constants
BASE_URL = "https://appliapay.com/"
AUTH = HTTPBasicAuth("admin", "123Give!@#")


def fetch_data_index(endpoint, devs, range):
    """Fetch data from the API."""
    response = requests.get(f"{BASE_URL}{endpoint}?range={range}&devs={devs}", auth=AUTH)
    response.raise_for_status()
    return response.json()


def fetch_and_process_data(devs, range):
    """Fetch and process data for display."""
    endpoint = "allDeviceDataFlet"

    try:
        data = fetch_data_index(endpoint, devs, range)
    except Exception as e:
        return None, None, None  # Handle API failure gracefully

    if not data or (data.get("totalkwh") == 0 and not data.get("runtime")):
        return None, None, None  # Handle empty data

    runtime = data.get("runtime", {})
    if not runtime:  # Handle empty runtime
        return None, None, None

    top_devices = sorted(runtime.items(), key=lambda x: x[1], reverse=True)[:3]
    sumRuntime = sum(runtime.values())
    totalKwh = data["totalkwh"]

    return sumRuntime, totalKwh, top_devices


def home_page(page: ft.Page):
    """Returns the home page UI components."""
    user_uid = page.session.get("user_id")
    doc_dic = fetch_user_data(user_uid)
    devices = doc_dic.get("devices", [])
    def handle_navigation(e):
        selected = e.control.selected_index
        if selected == 0:
            page.go("/")
        elif selected == 2:
            page.go("/logout")
    # Page Configuration
    page.title = "Powerpay Africa"
    page.drawer = ft.NavigationDrawer(
                on_change=handle_navigation,
                controls=[
                    ft.NavigationDrawerDestination(label="HOME", icon=ft.Icons.HOME),
                    ft.NavigationDrawerDestination(label="DEVICES", icon=ft.Icons.DEVELOPER_BOARD),
                    ft.NavigationDrawerDestination(label="LOGOUT", icon=ft.Icons.LOGOUT),
                ],
            )

    menu_icon_btn = ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=lambda e: setattr(page.drawer, "open", True),
            )

    page.appbar = ft.AppBar(
                title=ft.Text("Powerpay Africa"),
                center_title=True,
                bgcolor=ft.colors.GREEN,
                leading=menu_icon_btn,
            )
    page.update()
    def dropdown_changed(e):
        """Handle dropdown selection change."""
        kwh_value.value = "Refreshing..."
        runtime_value.value = "Refreshing..."
        energy_cost_value.value = "Refreshing..."
        emissions_value.value = "Refreshing..."
        page.update()
        
        value = value_map.get(dropdown.value, "9999999")
        runtime, totalKwh, top_devices = fetch_and_process_data(devices, value)

        if runtime is None or totalKwh is None:
            kwh_value.value = "N/A"
            runtime_value.value = "N/A"
            energy_cost_value.value = "N/A"
            emissions_value.value = "N/A"
        else:
            kwh_value.value = f"{round(totalKwh, 2)} kWh"
            runtime_value.value = f"{round(runtime, 1)} hours"
            energy_cost_value.value = f"KSH. {round((totalKwh * 23.0), 1)}"
            emissions_value.value = f"{round((totalKwh * 0.4999 * 0.28), 2)} kg CO₂"

        # Recreate DataTable with updated rows
        data_table.content = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Device ID", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Runtime (hrs)", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)),
            ],
            rows=generate_table_cells(top_devices),  # Updated rows
            heading_row_color=ft.Colors.GREEN,
            border=ft.border.all(1, ft.colors.GREY_300),
            column_spacing=10,
            divider_thickness=1,
            expand=True,
        )
        page.update()

    # Fetch initial data
    runtime, totalKwh, top_devices = fetch_and_process_data(devices, "180")

    # Dropdown for selecting time range
    dropdown = ft.Dropdown(
        label="Choose Time Range",
        on_change=dropdown_changed,
        options=[ft.dropdown.Option(k) for k in value_map.keys()],
        autofocus=False,
        value="All Time",
    )

    # Dynamic Text Elements
    kwh_value = ft.Text(f"{round(totalKwh, 2)} kWh" if totalKwh else "N/A", size=18, weight="bold", color="white")
    runtime_value = ft.Text(f"{round(runtime, 1)} hours" if runtime else "N/A", size=18, weight="bold", color="white")
    energy_cost_value = ft.Text(f"KSH. {round((totalKwh * 23.0), 1)}" if totalKwh else "N/A", size=18, weight="bold", color="white")
    emissions_value = ft.Text(f"{round((totalKwh * 0.4999 * 0.28), 2)} kg CO₂" if totalKwh else "N/A", size=18, weight="bold", color="white")

    # Styled Cards with Icons
    def create_card(icon, text, value, color):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=36, color="white"),
                        value,  # This is now a Text reference
                        ft.Text(text, size=14, color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=5,
                bgcolor=color,
                border_radius=10,
            )
        )

    kwh_card = create_card(ft.icons.BOLT, "Total Energy", kwh_value, "#FF5733")
    runtime_card = create_card(ft.icons.TIMER, "Total Runtime", runtime_value, "#33FF57")
    energy_cost_card = create_card(ft.icons.ATTACH_MONEY, "Energy Cost", energy_cost_value, "#3380FF")
    emissions_card = create_card(ft.icons.CLOUD, "CO₂ Emissions", emissions_value, "#FF33A8")

    # Generate table rows
    def generate_table_cells(devs):
        if not devs:  # Handle None or empty case
            return [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No Data", text_align=ft.TextAlign.CENTER, size=14, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text("-", text_align=ft.TextAlign.CENTER, size=14)),
                    ],
                    color=ft.colors.GREY_100,
                )
            ]

        return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(k, text_align=ft.TextAlign.CENTER, size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(f"{round(v, 1)} hrs", text_align=ft.TextAlign.CENTER, size=14)),
                ],
                color=ft.colors.with_opacity(0.1, ft.colors.BLUE_100 if i % 2 == 0 else ft.colors.GREY_100),
            )
            for i, (k, v) in enumerate(devs)
        ]

    # Ensure top_devices is not None before passing to function
    arr_cell = generate_table_cells(top_devices or [])


    # Data Table
    data_table = ft.Container(
        content=ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Device ID", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Runtime (hrs)", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)),
            ],
            rows=arr_cell,
            heading_row_color=ft.Colors.GREEN,
            border=ft.border.all(1, ft.colors.GREY_300),
            column_spacing=10,
            divider_thickness=1,
            expand=True,
    ),
        width=page.width,
        )

    # Return UI elements instead of modifying page directly
    return ft.Column(
        [
            # Time range selection dropdown
            ft.Container(dropdown, alignment=ft.alignment.top_right, padding=5),
            

            # Cards in Grid Layout
            ft.GridView(
                [
                    kwh_card,
                    runtime_card,
                    energy_cost_card,
                    emissions_card,
                ],
                runs_count=2,
                spacing=1,
                run_spacing=1,
            ),

            # Styled DataTable
            ft.Container(
                content=data_table,
                padding=5,
                border_radius=10,
                expand=True,
            ),
        ]
    )
