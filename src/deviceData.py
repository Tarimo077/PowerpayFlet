import flet as ft
import requests
from requests.auth import HTTPBasicAuth
import datetime

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


def fetch_data_index(deviceID, endpoint, time_range):
    response = requests.get(
        f"{BASE_URL}{endpoint}?device={deviceID}&range={time_range}", auth=AUTH
    )
    response.raise_for_status()
    return response.json()


def device_data_page(page: ft.Page, deviceID):
    data = fetch_data_index(deviceID, "deviceDataDjangoo", "180000")
    if not data or (data["runtime"] == 0 and not data["deviceMealCounts"] and not data["rawData"]):
        return ft.Text("No data available.", size=16, color=ft.colors.RED)

    # Function to format timestamps
    def format_timestamp(timestamp):
        return datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")

    # Function to generate a DataTable
    def generate_meal_table(meal_durations):
        columns = [
            ft.DataColumn(ft.Text("Start Time", weight=ft.FontWeight.BOLD, size=14)),
            ft.DataColumn(ft.Text("Duration", weight=ft.FontWeight.BOLD, size=14)),
            ft.DataColumn(ft.Text("End Time", weight=ft.FontWeight.BOLD, size=14)),
            ft.DataColumn(ft.Text("Total kWh", weight=ft.FontWeight.BOLD, size=14)),
            ft.DataColumn(ft.Text("Cost (Ksh)", weight=ft.FontWeight.BOLD, size=14)),
            ft.DataColumn(ft.Text("CO₂ Emissions", weight=ft.FontWeight.BOLD, size=14)),
        ]

        if not meal_durations:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("No Meal Data", text_align=ft.TextAlign.CENTER, size=14, weight=ft.FontWeight.BOLD)),
                        *[ft.DataCell(ft.Text("-", text_align=ft.TextAlign.CENTER, size=14)) for _ in range(5)],
                    ],
                    color=ft.colors.GREY_100,
                )
            ]
        else:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(format_timestamp(meal["startTime"]), text_align=ft.TextAlign.CENTER, size=14, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(f"{round(meal['mealDuration'] / 60, 1)} min", text_align=ft.TextAlign.CENTER, size=14)),
                        ft.DataCell(ft.Text(format_timestamp(meal["endTime"]), text_align=ft.TextAlign.CENTER, size=14)),
                        ft.DataCell(ft.Text(f"{meal['totalKwh']:.2f} kWh", text_align=ft.TextAlign.CENTER, size=14)),
                        ft.DataCell(ft.Text(f"KSH {round(meal['totalKwh'] * 23, 1)}", text_align=ft.TextAlign.CENTER, size=14)),
                        ft.DataCell(ft.Text(f"{round(meal['totalKwh'] * 0.4999 * 0.28, 2)} kg CO₂", text_align=ft.TextAlign.CENTER, size=14)),
                    ],
                    color=ft.colors.with_opacity(0.1, ft.colors.BLUE_100 if i % 2 == 0 else ft.colors.GREY_100),
                )
                for i, meal in enumerate(meal_durations)
            ]

        return ft.Container(content=ft.DataTable(
            columns=columns,
            rows=rows,
            heading_row_color=ft.Colors.GREEN,
            border=ft.border.all(1, ft.colors.GREY_300),
            column_spacing=10,
            divider_thickness=1,
            expand=True,
        ),
        width=page.width
        )

    def dropdown_changed(e):
        """Handle dropdown selection change."""
        kwh_value.value = "Refreshing..."
        runtime_value.value = "Refreshing..."
        energy_cost_value.value = "Refreshing..."
        emissions_value.value = "Refreshing..."
        page.update()

        value = value_map.get(dropdown.value, "9999999")
        new_data = fetch_data_index(deviceID, "deviceDataDjangoo", value)

        if not new_data or (new_data["runtime"] == 0 and not new_data["deviceMealCounts"] and not new_data["rawData"]):
            meal_table.content = ft.Text("No data available.", size=16, color=ft.colors.RED)
        else:
            totalKwh = new_data["sumKwh"]
            runtime = new_data["runtime"]
            kwh_value.value = f"{round(totalKwh, 2)} kWh"
            runtime_value.value = f"{round(runtime, 1)} hours"
            energy_cost_value.value = f"KSH. {round((totalKwh * 23.0), 1)}"
            emissions_value.value = f"{round((totalKwh * 0.4999 * 0.28), 2)} kg CO₂"
            meal_table.content = generate_meal_table(new_data["mealsWithDurations"])

        page.update()

    dropdown = ft.Dropdown(
        label="Choose Time Range",
        on_change=dropdown_changed,
        options=[ft.dropdown.Option(k) for k in value_map.keys()],
        autofocus=False,
        value="All Time",
    )

    totalKwh = data["sumKwh"]
    runtime = data["runtime"]

    kwh_value = ft.Text(f"{round(totalKwh, 2)} kWh", size=18, weight="bold", color="white")
    runtime_value = ft.Text(f"{round(runtime, 1)} hours", size=18, weight="bold", color="white")
    energy_cost_value = ft.Text(f"KSH. {round((totalKwh * 23.0), 1)}", size=18, weight="bold", color="white")
    emissions_value = ft.Text(f"{round((totalKwh * 0.4999 * 0.28), 2)} kg CO₂", size=18, weight="bold", color="white")

    def create_card(icon, text, value, color):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=36, color="white"),
                        value,
                        ft.Text(text, size=14, color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=5,
                bgcolor=color,
                border_radius=10
            )
        )

    kwh_card = create_card(ft.icons.BOLT, "Total Energy", kwh_value, "#FF5733")
    runtime_card = create_card(ft.icons.TIMER, "Total Runtime", runtime_value, "#33FF57")
    energy_cost_card = create_card(ft.icons.ATTACH_MONEY, "Energy Cost", energy_cost_value, "#3380FF")
    emissions_card = create_card(ft.icons.CLOUD, "CO₂ Emissions", emissions_value, "#FF33A8")

    meal_table = generate_meal_table(data["mealsWithDurations"])
    
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
                content=meal_table,
                padding=5,
                border_radius=10,
                expand=True,
                alignment=ft.alignment.top_center
            ),
        ], alignment=ft.MainAxisAlignment.START, spacing=5
    )
