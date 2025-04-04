import flet as ft
import os
import time
from firebase_config import fetch_user_data, upload_image, save_user_data, delete_old_image

def user_profile_page(page: ft.Page):
    selected_file_path = None  # Store selected file path

    def confirm_toggle(e):
        nonlocal selected_file_path
        page.close(dlg_confirm)
        page.update()

        user_info = fetch_user_data(page.session.get("user_id"))

        # Update user details
        user_info["email"] = email_input.value
        user_info["phone_number"] = phone_number_input.value
        user_info["display_name"] = display_name_input.value

        # Upload new profile picture if a file was selected
        if selected_file_path:
            user_id = page.session.get("user_id")
            old_image_url = page.session.get("profile_url")

            if old_image_url:
                delete_old_image(old_image_url)

            file_extension = os.path.splitext(selected_file_path)[-1]
            timestamp = int(time.time())  # Generate timestamp
            storage_path = f"{user_id}_{timestamp}{file_extension}"
            new_image_url = upload_image(selected_file_path, storage_path)
            print(f"Image Url: {new_image_url}")

            if new_image_url:
                page.session.set("profile_url", new_image_url)
                profile_img.src = new_image_url
                user_info["photo_url"] = new_image_url  # Update user data
                selected_file_text.value = ""  # Clear file name after upload

        # Save updated user data
        save_user_data(page.session.get("user_id"), user_info)

        # Update session values
        page.session.set("display_name", user_info["display_name"])
        page.session.set("email", user_info["email"])
        page.session.set("phone_number", user_info["phone_number"])
        profile_img.src = user_info["display_name"]
        page.update()

    def pick_file_result(e: ft.FilePickerResultEvent):
        nonlocal selected_file_path
        if e.files:
            selected_file_path = e.files[0].path  # Store file path
            selected_file_text.value = f"Selected file: {os.path.basename(selected_file_path)}"
            page.update()

    pick_file_dialog = ft.FilePicker(on_result=pick_file_result)
    page.overlay.append(pick_file_dialog)

    profile_img = ft.Image(src=page.session.get("profile_url"), fit=ft.ImageFit.COVER)
    
    selected_file_text = ft.Text("", size=12, color=ft.Colors.GREY)

    profile_pic_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=profile_img,
                    width=150, height=150,
                    border_radius=ft.border_radius.all(180),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(right=10, bottom=5)
                ),
                ft.TextButton(
                    "Change Profile Photo",
                    icon=ft.Icons.EDIT_ROUNDED,
                    icon_color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                    on_click=lambda _: pick_file_dialog.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
                ),
            ]),
            selected_file_text  # Display selected file name here
        ])
    )

    # Input Fields
    email_input = ft.TextField(label="Email", width=180, focused_border_color=ft.Colors.GREEN, label_style=ft.TextStyle(color=ft.Colors.GREEN))
    display_name_input = ft.TextField(label="Display Name", width=180, focused_border_color=ft.Colors.GREEN, label_style=ft.TextStyle(color=ft.Colors.GREEN))
    phone_number_input = ft.TextField(label="Phone Number", width=180, focused_border_color=ft.Colors.GREEN, label_style=ft.TextStyle(color=ft.Colors.GREEN))

    # Populate fields from session
    email_input.value = page.session.get("email")
    display_name_input.value = page.session.get("display_name")
    phone_number_input.value = page.session.get("phone_number")

    details_container = ft.Container(
        content=ft.Column([
            ft.Row([display_name_input, email_input], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([phone_number_input], alignment=ft.MainAxisAlignment.CENTER),
        ])
    )

    update_button = ft.Container(
        content=ft.TextButton(
            "UPDATE",
            icon=ft.Icons.UPLOAD_ROUNDED,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
            icon_color=ft.Colors.WHITE,
            on_click=lambda _: page.open(dlg_confirm),
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(20),
    )

    dlg_confirm = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Action"),
        content=ft.Text("Are you sure you want to update your profile?"),
        actions=[ft.TextButton("Yes", on_click=confirm_toggle), ft.TextButton("No", on_click=lambda _: page.close(dlg_confirm))],
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(name=ft.Icons.PERSON_PIN_ROUNDED, color=ft.Colors.GREEN, size=24), ft.Text("My Profile", size=24)]),
            profile_pic_container,
            details_container,
            update_button,
        ], alignment=ft.MainAxisAlignment.CENTER)
    )
