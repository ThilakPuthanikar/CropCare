from typing import Set
from fastapi import HTTPException, UploadFile, status

ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

ALLOWED_PDF_MIME_TYPES = {"application/pdf"}
ALLOWED_PDF_EXTENSIONS = {".pdf"}
MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


async def validate_upload_file(
    file: UploadFile,
    allowed_mimes: Set[str],
    allowed_exts: Set[str],
    max_size: int,
    file_type_label: str = "File",
) -> bytes:
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No {file_type_label.lower()} provided.",
        )

    content_type = (file.content_type or "").lower()
    if content_type not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{content_type}' for {file_type_label.lower()} upload.",
        )

    ext = ""
    if "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}' for {file_type_label.lower()} upload.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded {file_type_label.lower()} is empty.",
        )

    if len(contents) > max_size:
        max_size_mb = max_size // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{file_type_label} size ({len(contents)} bytes) exceeds limit of {max_size_mb}MB.",
        )

    return contents
