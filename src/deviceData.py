import flet as ft
import requests
from requests.auth import HTTPBasicAuth
import datetime
import pandas as pd

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
    progress_ring = ft.Container(ft.ProgressRing(color=ft.Colors.GREEN), alignment=ft.alignment.center, expand=True, visible=False)
    page.title = f"Powerpay Africa: {deviceID} data"
    page.update()
    data = fetch_data_index(deviceID, "deviceDataDjangoo", "9999999")
    if not data or (data["runtime"] == 0 and not data["deviceMealCounts"] and not data["rawData"]):
        return ft.Text("No data available.", size=16, color=ft.Colors.RED)

    # Function to format timestamps
    def format_timestamp(timestamp):
        return datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    

    # Function to generate a DataTable
    def generate_meal_table(meal_durations):
        meal_durations = reversed(meal_durations)
        df = pd.DataFrame(meal_durations)

        if df.empty:
            df = pd.DataFrame([{"Start Time": "No Meal Data", "Duration": "N/A", "End Time": "N/A", "Total kWh": "N/A"}])
        else:
            df["From"] = df["startTime"].apply(format_timestamp)
            df["Duration"] = df["mealDuration"].apply(lambda x: f"{round(x / 60, 1)} min")
            df["To"] = df["endTime"].apply(format_timestamp)
            df["Energy"] = df["totalKwh"].apply(lambda x: f"{x:.2f} kWh")

            df = df[["From", "Duration", "To", "Energy"]]

        rows_per_page = 10
        total_rows = len(df)
        total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)
        current_page = ft.Ref()  # Correct
        current_page.value = 0   # Set initial value

        meal_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(col)) for col in df.columns],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            heading_row_color=ft.Colors.GREEN,
            column_spacing=5,
            divider_thickness=1, 
            expand=True
        )

        page_text = ft.Text(f"Page {current_page.value + 1} of {total_pages}")

        def update_table():
            start_idx = current_page.value * rows_per_page
            end_idx = start_idx + rows_per_page
            meal_table.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(df.iloc[i, j]))) for j in range(len(df.columns))
                ]) for i in range(start_idx, min(end_idx, total_rows))
            ]
            page_text.value = f"Page {current_page.value + 1} of {total_pages}"
            
            # Show/Hide buttons dynamically
            prev_button.visible = current_page.value > 0
            next_button.visible = current_page.value < total_pages - 1
            
            page.update()

        def go_to_next_page(e):
            if current_page.value < total_pages - 1:
                current_page.value += 1
                update_table()

        def go_to_prev_page(e):
            if current_page.value > 0:
                current_page.value -= 1
                update_table()

        # Define buttons with visibility control
        prev_button = ft.IconButton(ft.Icons.SKIP_PREVIOUS_ROUNDED, on_click=go_to_prev_page, visible=False, icon_color=ft.Colors.GREEN)
        next_button = ft.IconButton(ft.Icons.SKIP_NEXT_ROUNDED, on_click=go_to_next_page, visible=total_pages > 1, icon_color=ft.Colors.GREEN)

        pagination_controls = ft.Container(content=ft.Row(
            [
                prev_button,
                page_text,
                next_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            expand=True,
        ), padding=ft.padding.only(bottom=30), expand=True)

        update_table()

        return ft.Container(meal_table, width=page.width, expand=True), pagination_controls


    def dropdown_changed(e):
        # Show refreshing state
        for val in [kwh_value, runtime_value, energy_cost_value, emissions_value, meal_count_value]:
            val.value = "Refreshing..."
        
        progress_ring.visible = True
        page.update()  # Update UI once

        value = value_map.get(dropdown.value, "9999999")
        new_data = fetch_data_index(deviceID, "deviceDataDjangoo", value)

        if not new_data or (new_data["runtime"] == 0 and not new_data["deviceMealCounts"] and not new_data["rawData"]):
            
           # page.go(f"/nodata/{deviceID}")
            kwh_value.value = "N/A"
            runtime_value.value = "N/A"
            energy_cost_value.value = "N/A"
            emissions_value.value = "N/A"
            meal_count_value.value = "N/A"
            
            #meal_table.content.clear()
            table_widget, pagination = generate_meal_table(new_data["mealsWithDurations"])
            page_controls.content = pagination
            meal_table.content = table_widget
        else:
            # Update values with actual data
            totalKwh = new_data.get("sumKwh", 0)
            runtime = new_data.get("runtime", 0)
            meal_counts = new_data.get("deviceMealCounts")
            
            kwh_value.value = f"{round(totalKwh, 2)} kWh"
            runtime_value.value = f"{round(runtime, 1)} hours"
            energy_cost_value.value = f"KSH. {round((totalKwh * 23.0), 1)}"
            emissions_value.value = f"{round((totalKwh * 0.4999 * 0.28), 2)} kg CO₂"
            meal_count_value.value = f"{str(meal_counts[deviceID]['count'])} meals"
            
            if "mealsWithDurations" in new_data:
                table_widget, pagination = generate_meal_table(new_data["mealsWithDurations"])
                page_controls.content = pagination
                meal_table.content = table_widget

            
            #no_data_text.value = ""  # Hide "No data available" if there is data
        progress_ring.visible = False
        page.update()  # Perform final UI update


    dropdown = ft.Dropdown(
        label="Choose Time Range",
        on_change=dropdown_changed,
        options=[ft.dropdown.Option(k) for k in value_map.keys()],
        autofocus=False,
        value="All Time",
        border_color=ft.Colors.GREEN,
        border_width=2,
        menu_height=300
    )

    def confirm_toggle(e):
        page.close(dlg_confirm)
        switch_changed(e)

    def cancel_toggle(e):
        page.close(dlg_confirm)
        statusSwitch.value = not statusSwitch.value  # Revert to previous state
        statusSwitch.update()

    def open_confirm_dialog(e):
        dlg_confirm.content=ft.Text(f"Are you sure you want to {'activate' if statusSwitch.value else 'deactivate'} {deviceID} ?")
        page.open(dlg_confirm)


    def switch_changed(e):
        try:
            response = requests.post("https://appliapay.com/changeStatus", json={
                "selectedDev": deviceID,
                "status": not statusSwitch.value  # Use current switch value
            })
            response_data = response.json()

            if response.status_code == 200:
                # ✅ Extract updated values from API response
                new_device_id = response_data.get("selectedDev", deviceID)
                new_status = response_data.get("status", statusSwitch.value)  # Default to current status
                
                switchMessage = f"Turn off {new_device_id}" if new_status else f"Turn On {new_device_id}"
                statusSwitch.value = new_status
                statusSwitch.label = switchMessage
                page.open(ft.SnackBar(ft.Text(f"{new_device_id} turned on" if new_status else f"{new_device_id} turned off", text_align=ft.TextAlign.CENTER), bgcolor=ft.Colors.GREEN if new_status else ft.Colors.RED))
                page.update()
            else:
                print("Error:", response_data)
        except Exception as ex:
            print("Request failed:", ex)

    # Initialize the switch
    switchMessage = f"Turn off {deviceID}" if data["status"] else f"Turn On {deviceID}"
    statusSwitch = ft.Switch(
        label=switchMessage, 
        active_color=ft.Colors.GREY_300, 
        active_track_color=ft.Colors.GREEN, 
        value=data["status"], 
        label_position=ft.LabelPosition.LEFT,
        on_change=open_confirm_dialog
    )
    dlg_confirm = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Action"),
        content=ft.Text(f"Are you sure you want to {'deactivate' if statusSwitch.value else 'activate'} {deviceID} ?"),
        actions=[
            ft.TextButton("Yes", on_click=confirm_toggle),
            ft.TextButton("No", on_click=cancel_toggle),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    totalKwh = data["sumKwh"]
    runtime = data["runtime"]
    meal_counts = data["deviceMealCounts"]

    kwh_value = ft.Text(f"{round(totalKwh, 2)} kWh", size=18, weight="bold", color="white")
    runtime_value = ft.Text(f"{round(runtime, 1)} hours", size=18, weight="bold", color="white")
    energy_cost_value = ft.Text(f"KSH. {round((totalKwh * 23.0), 1)}", size=18, weight="bold", color="white")
    emissions_value = ft.Text(f"{round((totalKwh * 0.4999 * 0.28), 2)} kg CO₂", size=18, weight="bold", color="white")
    meal_count_value = ft.Text(f"{str(meal_counts[deviceID]['count'])} meals", size=18, weight="bold", color="white")
    device_serial_value = ft.Text(f"{deviceID}", size=18, weight="bold", color="white")

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

    kwh_card = create_card(ft.Icons.BOLT, "Total Energy", kwh_value, "#FF5733")
    runtime_card = create_card(ft.Icons.TIMER, "Total Runtime", runtime_value, "#33FF57")
    energy_cost_card = create_card(ft.Icons.ATTACH_MONEY, "Energy Cost", energy_cost_value, "#3380FF")
    emissions_card = create_card(ft.Icons.CLOUD, "CO₂ Emissions", emissions_value, "#FF33A8")
    meal_count_card = create_card(ft.Icons.FOOD_BANK_ROUNDED, "Total Meals", meal_count_value, "#900C3F")
    device_card = create_card(ft.Icons.DEVELOPER_BOARD_ROUNDED, "Serial Number", device_serial_value, "#B51BFD")

    meal_table, page_controls = generate_meal_table(data["mealsWithDurations"])
    
    # Return UI elements instead of modifying page directly
    return ft.Stack([ft.Container(
    content=ft.Column(
        [
            # Time range selection dropdown
            ft.Container(dropdown, alignment=ft.alignment.top_right, padding=5),
            ft.Container(statusSwitch, alignment=ft.alignment.top_right, padding=5),

            # Cards in Grid Layout
            ft.GridView(
                [   
                    device_card,
                    meal_count_card,
                    kwh_card,
                    runtime_card,
                    energy_cost_card,
                    emissions_card,
                ],
                runs_count=2,
                spacing=1,
                run_spacing=1,
            ),

            # Styled DataTable with Heading
            ft.Container(content=ft.Text(
                "Cooking Events", 
                size=20, 
                weight=ft.FontWeight.BOLD, 
                text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center),

            meal_table,
            page_controls
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=5,
        scroll=ft.ScrollMode.AUTO,
        expand=True,  # Allows column to take available space and scroll
    ),
    expand=True  # Ensures the container also expands to allow scrolling
), progress_ring], expand=True)

