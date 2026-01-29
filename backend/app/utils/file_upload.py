"""File upload utility for handling document and image uploads."""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
}

MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes


def get_upload_dir(subfolder: str = "") -> Path:
    """Get upload directory path, creating it if necessary."""
    base_dir = Path(settings.UPLOAD_DIR)
    if subfolder:
        upload_dir = base_dir / subfolder
    else:
        upload_dir = base_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


async def save_upload_file(
    file: UploadFile,
    subfolder: str = "documents",
    allowed_types: Optional[dict] = None,
) -> str:
    """Save an uploaded file and return the relative URL path."""
    if allowed_types is None:
        allowed_types = ALLOWED_IMAGE_TYPES

    # Validate content type
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' not allowed. Allowed: {', '.join(allowed_types.keys())}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Generate unique filename
    ext = allowed_types[file.content_type]
    filename = f"{uuid.uuid4().hex}{ext}"

    # Save file
    upload_dir = get_upload_dir(subfolder)
    file_path = upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(content)

    # Return relative URL
    return f"/uploads/{subfolder}/{filename}"


def delete_upload_file(file_url: str) -> bool:
    """Delete an uploaded file by its URL path."""
    if not file_url:
        return False

    # Convert URL to file path
    relative_path = file_url.lstrip("/")
    file_path = Path(relative_path)

    if file_path.exists():
        file_path.unlink()
        return True
    return False
