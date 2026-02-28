"""Image processing utilities for the photo gallery.

Handles EXIF rotation, resizing, thumbnail generation, HEIC conversion,
and metadata stripping for uploaded photos.
"""

import io
import uuid
from pathlib import Path

from PIL import Image, ImageOps

PHOTOS_DIR = Path("/data/photos")
ORIGINALS_DIR = PHOTOS_DIR / "originals"
THUMBS_DIR = PHOTOS_DIR / "thumbs"

MAX_ORIGINAL_SIZE = 2048
THUMB_SIZE = 400
ORIGINAL_QUALITY = 85
THUMB_QUALITY = 80

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}


def ensure_dirs():
    """Create photo storage directories if they don't exist."""
    ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)


def _register_heif():
    """Register HEIF/HEIC opener with Pillow if available."""
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    except ImportError:
        pass


_register_heif()


def process_upload(file_bytes: bytes) -> tuple[str, int, int, int]:
    """Process an uploaded image file.

    Fixes EXIF rotation, resizes to max 2048px, generates a 400px thumbnail,
    and strips EXIF metadata (including GPS data) for privacy.

    Args:
        file_bytes: Raw bytes of the uploaded image file.

    Returns:
        Tuple of (photo_id, width, height, file_size) where photo_id is a
        UUID4 hex string used as the filename (without extension).

    Raises:
        ValueError: If the image cannot be opened or processed.
    """
    photo_id = uuid.uuid4().hex

    try:
        img = Image.open(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ValueError(f"Cannot open image: {exc}") from exc

    # Fix EXIF rotation (critical for phone photos)
    img = ImageOps.exif_transpose(img)

    # Convert to RGB if needed (e.g. RGBA PNGs, palette images)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Resize original to max 2048px on longest side
    img.thumbnail((MAX_ORIGINAL_SIZE, MAX_ORIGINAL_SIZE), Image.LANCZOS)
    width, height = img.size

    # Save original
    original_path = ORIGINALS_DIR / f"{photo_id}.jpg"
    img.save(original_path, "JPEG", quality=ORIGINAL_QUALITY)
    file_size = original_path.stat().st_size

    # Generate thumbnail
    thumb = img.copy()
    thumb.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
    thumb_path = THUMBS_DIR / f"{photo_id}.jpg"
    thumb.save(thumb_path, "JPEG", quality=THUMB_QUALITY)

    return photo_id, width, height, file_size


def delete_photo_files(photo_id: str):
    """Delete original and thumbnail files for a photo.

    Args:
        photo_id: UUID hex string identifying the photo.
    """
    original_path = ORIGINALS_DIR / f"{photo_id}.jpg"
    thumb_path = THUMBS_DIR / f"{photo_id}.jpg"
    original_path.unlink(missing_ok=True)
    thumb_path.unlink(missing_ok=True)
