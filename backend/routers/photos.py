"""Photo gallery API endpoints.

Handles photo uploads, listing, and deletion for the wedding gallery.
"""

import time
from collections import defaultdict
from math import ceil

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from db import get_db
from image_utils import (
    ALLOWED_MIME_TYPES,
    delete_photo_files,
    process_upload,
)
from models import Photo
from schemas import PhotoListResponse, PhotoResponse

router = APIRouter(prefix="/api/photos", tags=["photos"])

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
RATE_LIMIT_MAX = 30  # max uploads per window per IP

# Simple in-memory rate limiter: {ip: [timestamp, ...]}
_upload_timestamps: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(ip: str):
    """Check and enforce upload rate limit for an IP address.

    Args:
        ip: Client IP address.

    Raises:
        HTTPException: 429 if rate limit exceeded.
    """
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW
    timestamps = _upload_timestamps[ip]
    # Prune old entries
    _upload_timestamps[ip] = [t for t in timestamps if t > cutoff]
    if len(_upload_timestamps[ip]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Upload rate limit exceeded. Try again later.")
    _upload_timestamps[ip].append(now)


def _photo_to_response(photo: Photo) -> PhotoResponse:
    """Convert a Photo model instance to a PhotoResponse schema.

    Args:
        photo: Photo ORM model instance.

    Returns:
        PhotoResponse with computed thumb_url and full_url.
    """
    return PhotoResponse(
        id=photo.id,
        original_filename=photo.original_filename,
        uploader_name=photo.uploader_name,
        caption=photo.caption,
        width=photo.width,
        height=photo.height,
        thumb_url=f"/photos/thumbs/{photo.id}.jpg",
        full_url=f"/photos/originals/{photo.id}.jpg",
        created_at=photo.created_at,
    )


@router.post("", response_model=PhotoResponse)
async def upload_photo(
    request: Request,
    file: UploadFile = File(...),
    uploader_name: str | None = Form(None),
    caption: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a photo to the gallery.

    Args:
        request: FastAPI request (for client IP).
        file: Uploaded image file (multipart).
        uploader_name: Optional name of the uploader.
        caption: Optional photo caption.
        db: Database session.

    Returns:
        PhotoResponse with the uploaded photo details.

    Raises:
        HTTPException: 400 for invalid file type/size, 429 for rate limit.
    """
    client_ip = request.headers.get("x-real-ip", request.client.host)
    _check_rate_limit(client_ip)

    # Validate content type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"File type not allowed: {content_type}")

    # Read and validate size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 15MB.")

    # Process image
    try:
        photo_id, width, height, file_size = process_upload(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Save metadata to DB
    photo = Photo(
        id=photo_id,
        original_filename=file.filename or "unknown",
        uploader_name=uploader_name.strip() if uploader_name else None,
        caption=caption.strip() if caption else None,
        mime_type=content_type,
        file_size=file_size,
        width=width,
        height=height,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)

    return _photo_to_response(photo)


@router.get("", response_model=PhotoListResponse)
def list_photos(
    page: int = 1,
    per_page: int = 20,
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """List photos with pagination, newest first.

    Args:
        page: Page number (1-indexed).
        per_page: Number of photos per page (max 100).
        search: Optional search string to filter by uploader_name or caption.
        db: Database session.

    Returns:
        PhotoListResponse with paginated photo list.
    """
    per_page = min(per_page, 100)
    page = max(page, 1)

    query = db.query(Photo)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Photo.uploader_name.ilike(pattern),
                Photo.caption.ilike(pattern),
            )
        )

    total = query.with_entities(func.count(Photo.id)).scalar() or 0
    total_pages = ceil(total / per_page) if total > 0 else 1

    photos = (
        query
        .order_by(Photo.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return PhotoListResponse(
        photos=[_photo_to_response(p) for p in photos],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.delete("/{photo_id}")
def delete_photo(photo_id: str, db: Session = Depends(get_db)):
    """Delete a photo by ID (admin use).

    Args:
        photo_id: UUID hex string of the photo to delete.
        db: Database session.

    Returns:
        Confirmation message.

    Raises:
        HTTPException: 404 if photo not found.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    delete_photo_files(photo_id)
    db.delete(photo)
    db.commit()

    return {"detail": "Photo deleted"}
