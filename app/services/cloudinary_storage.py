import os
import uuid

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask import current_app
from werkzeug.utils import secure_filename


def configure_cloudinary(app):
    cloud_name = app.config.get("CLOUDINARY_CLOUD_NAME")
    api_key = app.config.get("CLOUDINARY_API_KEY")
    api_secret = app.config.get("CLOUDINARY_API_SECRET")

    if not (cloud_name and api_key and api_secret):
        return False

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )
    return True


def cloudinary_enabled():
    return bool(
        current_app.config.get("CLOUDINARY_CLOUD_NAME")
        and current_app.config.get("CLOUDINARY_API_KEY")
        and current_app.config.get("CLOUDINARY_API_SECRET")
    )


def _save_local_copy(file_storage, folder_key):
    folder = current_app.config[folder_key]
    os.makedirs(folder, exist_ok=True)

    original_name = secure_filename(file_storage.filename or "")
    extension = original_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    file_storage.save(os.path.join(folder, filename))
    return {
        "public_id": None,
        "filename": filename,
    }


def store_media(file_storage, folder, folder_key, resource_type="image"):
    if not file_storage or not file_storage.filename:
        return None

    if cloudinary_enabled():
        kwargs = {
            "folder": folder,
            "resource_type": resource_type,
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        if resource_type == "raw":
            original_name = secure_filename(file_storage.filename or "")
            if "." in original_name:
                base_name, ext = original_name.rsplit(".", 1)
                kwargs["public_id"] = f"{folder}/{base_name}_{uuid.uuid4().hex[:8]}.{ext}"
                del kwargs["folder"]
                del kwargs["use_filename"]
                del kwargs["unique_filename"]

        upload_result = cloudinary.uploader.upload(file_storage, **kwargs)
        return {
            "public_id": upload_result["public_id"],
            "filename": secure_filename(file_storage.filename or ""),
            "secure_url": upload_result.get("secure_url"),
        }

    return _save_local_copy(file_storage, folder_key)


def delete_media(public_id=None, filename=None, folder_key=None, resource_type="image"):
    if public_id and cloudinary_enabled():
        cloudinary.uploader.destroy(public_id, resource_type=resource_type, invalidate=True)
        return

    if filename and folder_key:
        file_path = os.path.join(current_app.config[folder_key], filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as exc:
                print(f"Error removing uploaded file: {exc}")


def build_media_url(public_id=None, filename=None, local_prefix=None, resource_type="image", default_url=None, **kwargs):
    if public_id and cloudinary_enabled():
        return cloudinary_url(public_id, resource_type=resource_type, secure=True, **kwargs)[0]

    if filename and local_prefix:
        return f"/static/{local_prefix}/{filename}"

    return default_url
