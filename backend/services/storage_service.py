import os
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

import cloudinary
import cloudinary.uploader
from ..config.settings import settings

logger = logging.getLogger(__name__)


class BaseStorageService(ABC):
    @abstractmethod
    async def upload_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str = "cropcare",
        content_type: Optional[str] = None,
    ) -> str:
        """Upload a file from bytes and return the public URL."""
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        """Delete a file by its URL or public identifier."""
        pass


class CloudinaryStorageService(BaseStorageService):
    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )

    async def upload_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str = "cropcare",
        content_type: Optional[str] = None,
    ) -> str:
        try:
            # Cloudinary accepts bytes directly or file-like object
            response = cloudinary.uploader.upload(
                file_bytes,
                folder=folder,
                resource_type="auto",
            )
            secure_url = response.get("secure_url") or response.get("url")
            if not secure_url:
                raise RuntimeError("Cloudinary did not return a secure URL.")
            return secure_url
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise RuntimeError(f"File upload service failed: {e}")

    async def delete_file(self, file_url: str) -> bool:
        try:
            # Extract public_id from cloudinary URL
            parts = file_url.split("/")
            if "upload" in parts:
                idx = parts.index("upload")
                # public_id is everything after upload/vXXX/ or upload/
                sub_parts = parts[idx + 1 :]
                if sub_parts and sub_parts[0].startswith("v"):
                    sub_parts = sub_parts[1:]
                public_id_with_ext = "/".join(sub_parts)
                public_id, _ = os.path.splitext(public_id_with_ext)
                cloudinary.uploader.destroy(public_id)
                return True
            return False
        except Exception as e:
            logger.error(f"Cloudinary delete failed: {e}")
            return False


class LocalStorageService(BaseStorageService):
    def __init__(self):
        self.upload_dir = Path("static/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str = "cropcare",
        content_type: Optional[str] = None,
    ) -> str:
        target_dir = self.upload_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
        file_path = target_dir / unique_name
        file_path.write_bytes(file_bytes)
        return f"/static/uploads/{folder}/{unique_name}"

    async def delete_file(self, file_url: str) -> bool:
        try:
            if file_url.startswith("/static/uploads/"):
                rel_path = file_url.lstrip("/")
                full_path = Path(rel_path)
                if full_path.exists():
                    full_path.unlink()
                    return True
            return False
        except Exception as e:
            logger.error(f"Local file delete failed: {e}")
            return False


def get_storage_service() -> BaseStorageService:
    if (
        settings.CLOUDINARY_CLOUD_NAME
        and settings.CLOUDINARY_API_KEY
        and settings.CLOUDINARY_API_SECRET
    ):
        return CloudinaryStorageService()
    if settings.ENVIRONMENT.lower() == "production":
        logger.warning(
            "Production environment detected but Cloudinary credentials are missing. Falling back to LocalStorageService."
        )
    return LocalStorageService()
