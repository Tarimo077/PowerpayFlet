import flet as ft
import os
from datetime import datetime
from firebase_config import fetch_user_data, upload_image, save_user_data, delete_old_image

def user_profile_page(page: ft.Page):

    def confirm_toggle(e):
        # Close confirmation dialog properly
        page.close(dlg_confirm)
        page.update()

        # Fetch latest user info
        user_info = fetch_user_data(page.session.get("user_id"))

        # Update user details with input field values
        user_info["email"] = email_input.value
        user_info["phone_number"] = phone_number_input.value
        user_info["display_name"] = display_name_input.value

        # Save updated user data
        save_user_data(page.session.get("user_id"), user_info)

        # Update session values
        page.session.set("display_name", user_info["display_name"])
        page.session.set("email", user_info["email"])
        page.session.set("phone_number", user_info["phone_number"])
        
        # Ensure 'created_at' is not None before setting
        created_at = user_info.get("created_time", "N/A")
        page.session.set("created_at", created_at)

        # Update input fields with new session data
        email_input.value = page.session.get("email")
        display_name_input.value = page.session.get("display_name")
        phone_number_input.value = page.session.get("phone_number")
        page.update()

    
    def cancel_toggle(e):
        email_input.value = page.session.get("email")
        display_name_input.value = page.session.get("display_name")
        phone_number_input.value = page.session.get("phone_number")
        page.update()
        page.close(dlg_confirm)


    dlg_confirm = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Action"),
        content=ft.Text(f"Are you sure you want to make these changes?"),
        actions=[
            ft.TextButton("Yes", on_click=confirm_toggle),
            ft.TextButton("No", on_click=cancel_toggle),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    error_snack_bar = ft.SnackBar(bgcolor=ft.Colors.RED, content=ft.Text("No changes detected", size=14, text_align=ft.TextAlign.CENTER))
    def edit_details(e):
        if email_input.value == page.session.get("email") and phone_number_input.value == page.session.get("phone_number") and display_name_input.value == page.session.get("display_name"):
            page.open(error_snack_bar)
            return
        page.open(dlg_confirm)
         

    def pick_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            local_image_path = e.files[0].path  # Get the selected file path
            file_extension = os.path.splitext(local_image_path)[-1]  # Extract file extension
            user_id = page.session.get("user_id")  # Get user_id from session
            old_image_url = page.session.get("profile_url")  # Get existing profile picture URL

            if old_image_url:
                delete_old_image(old_image_url)  # Step 1: Delete old image from storage

            # Step 2: Upload new image with correct file extension
            storage_path = f"{user_id}{file_extension}"
            print(f"Storage Path: {storage_path} /n Local Path: {local_image_path}")
            new_image_url = upload_image(local_image_path, storage_path)
            print(new_image_url)

            if new_image_url:
                # Step 3: Update session
                print(page.session.get("profile_url"))
                page.session.set("profile_url", new_image_url)
                profile_img.src = new_image_url
                print(page.session.get("profile_url"))
                page.update()

                # Step 4: Update Firestore user document
                user_info = fetch_user_data(user_id)  # Get existing user data
                user_info["photo_url"] = new_image_url
                save_user_data(user_id, user_info)

                print("✅ Profile photo updated successfully!")


        # Create FilePicker
    pick_file_dialog = ft.FilePicker(on_result=pick_file_result)
    page.overlay.append(pick_file_dialog)  # ✅ Register with page.overlay
    profile_img = ft.Image(
                    src=page.session.get("profile_url"),
                    fit=ft.ImageFit.COVER
                ) 
    profile_pic_container = ft.Container(
        content=ft.Row([
            ft.Container(
                content=profile_img,
                width=150,
                height=150,
                border_radius=ft.border_radius.all(180),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                alignment=ft.alignment.center,
                margin=ft.margin.only(right=10, bottom=5)
            ),
            ft.TextButton(
                "Change Profile Photo", 
                icon=ft.Icons.EDIT_ROUNDED, 
                icon_color=ft.Colors.WHITE,
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE, alignment=ft.alignment.center),
                on_click=lambda _: pick_file_dialog.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
            )
        ]), padding=ft.padding.all(10), margin=ft.margin.all(10)
    )
        # Input Fields
    email_input = ft.TextField(
        label="Email",
        width=180,
        focused_border_color=ft.Colors.GREEN,
        #color=ft.Colors.BLACK,
        label_style=ft.TextStyle(color=ft.colors.GREEN),
        keyboard_type=ft.KeyboardType.EMAIL
    )

    display_name_input = ft.TextField(
        label="Display Name",
        width=180,
        focused_border_color=ft.Colors.GREEN,
        #color=ft.Colors.BLACK,
        label_style=ft.TextStyle(color=ft.colors.GREEN)
    )

    phone_number_input = ft.TextField(
        label="Phone Number",
        width=180,
        focused_border_color=ft.Colors.GREEN,
        #color=ft.Colors.BLACK,
        label_style=ft.TextStyle(color=ft.colors.GREEN),
        keyboard_type=ft.KeyboardType.NUMBER
    )
    created_text = ft.TextField(
        label="Created at",
        width=180,
        focused_border_color=ft.Colors.GREEN,
        #color=ft.Colors.BLACK,
        label_style=ft.TextStyle(color=ft.colors.GREEN),
        keyboard_type=ft.KeyboardType.DATETIME,
        read_only=True
    )
    email_input.value = page.session.get("email")
    display_name_input.value = page.session.get("display_name")
    phone_number_input.value = page.session.get("phone_number")
    created_text.value = page.session.get("created_at").strftime("%Y-%m-%d %H:%M:%S")
    

    # Details Container
    details_container = ft.Container(
        content=ft.Column(
            [
                ft.Row([display_name_input, email_input], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([phone_number_input, created_text], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=40,  # Adds spacing between rows
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

    # Update Button (Centered)
    update_button = ft.Container(
        content=ft.TextButton(
            "UPDATE",
            icon=ft.icons.UPLOAD_ROUNDED,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.GREEN,
                color=ft.colors.WHITE,
            ),
            icon_color=ft.colors.WHITE,
            on_click=edit_details,
        ),
        alignment=ft.alignment.center,  # Center the button
        padding=ft.padding.all(20),
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row([ft.Icon(name=ft.Icons.PERSON_PIN_ROUNDED, color=ft.Colors.GREEN, size=24), ft.Text("My Profile", size=24)]),
                profile_pic_container,
                details_container,
                update_button,  # Button properly aligned
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )