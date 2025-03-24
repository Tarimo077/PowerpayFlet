import flet as ft
import time


def no_data_page(page: ft.Page, deviceID):
    dlg_alert = ft.AlertDialog(
                modal=False,
                title=ft.Text("Error"),
                content=ft.Text(f"No data for the selected time range. Reloading page..."),
            )
    page.open(dlg_alert)
    time.sleep(3)
    page.update()
    page.close(dlg_alert)
    page.update()
    page.go(f"/device/{deviceID}")
    return