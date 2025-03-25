import flet as ft
import os
from firebase_config import fetch_user_data, upload_image, save_user_data, delete_old_image

def user_profile_page(page: ft.Page):

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
        ])
    )

    return profile_pic_container
