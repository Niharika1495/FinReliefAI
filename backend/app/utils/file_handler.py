import os
import re
import uuid
from fastapi import UploadFile, HTTPException, status

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes filenames to prevent directory traversal and command injection.
    """
    base = os.path.basename(filename)
    base = re.sub(r'[^a-zA-Z0-9._-]', '_', base)
    return base

def save_upload_file(upload_file: UploadFile) -> str:
    """
    Validates mime type and file size, sanitizes the filename, 
    and saves the uploaded file to app/static/uploads/.
    Returns the absolute path of the saved file.
    """
    if upload_file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {upload_file.content_type}. Only PDF, PNG, JPEG are allowed."
        )

    # Read content to check size
    content = upload_file.file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 10MB limit."
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    safe_name = sanitize_filename(upload_file.filename)
    name, ext = os.path.splitext(safe_name)
    # Generate unique filename to avoid collision
    safe_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(content[:MAX_FILE_SIZE])

    return os.path.abspath(file_path)
