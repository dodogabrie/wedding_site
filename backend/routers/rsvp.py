"""RSVP API endpoints for managing guest attendance."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models import Family, Guest
from schemas import (
    GuestResponse,
    GuestUpdate,
    FamilyResponse,
    FamilyGuestsUpdate,
    RSVPStats,
)

router = APIRouter(prefix="/api", tags=["rsvp"])


@router.get("/families", response_model=list[FamilyResponse])
def list_families(db: Session = Depends(get_db)):
    """Get all families with their guests.

    Args:
        db: Database session

    Returns:
        List of families with nested guest information
    """
    return db.query(Family).all()


@router.get("/guests", response_model=list[GuestResponse])
def list_guests(db: Session = Depends(get_db)):
    """Get all individual guests (those without a family).

    Args:
        db: Database session

    Returns:
        List of guests without family association
    """
    return db.query(Guest).filter(Guest.family_id.is_(None)).all()


@router.patch("/guests/{guest_id}", response_model=GuestResponse)
def update_guest(guest_id: int, update: GuestUpdate, db: Session = Depends(get_db)):
    """Update a guest's RSVP status.

    Args:
        guest_id: ID of the guest to update
        update: New attendance status and optional dietary notes
        db: Database session

    Returns:
        Updated guest information

    Raises:
        HTTPException: If guest not found
    """
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    if update.attending is not None:
        guest.attending = update.attending
    if update.dietary_notes is not None:
        guest.dietary_notes = update.dietary_notes

    db.commit()
    db.refresh(guest)
    return guest


@router.patch("/families/{family_id}/guests", response_model=FamilyResponse)
def update_family_guests(
    family_id: int, update: FamilyGuestsUpdate, db: Session = Depends(get_db)
):
    """Bulk update attendance for all guests in a family.

    Args:
        family_id: ID of the family
        update: Dict mapping guest_id to new attendance status
        db: Database session

    Returns:
        Updated family with guest information

    Raises:
        HTTPException: If family not found
    """
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    for guest_id, attending in update.guest_updates.items():
        guest = db.query(Guest).filter(
            Guest.id == guest_id, Guest.family_id == family_id
        ).first()
        if guest:
            guest.attending = attending

    db.commit()
    db.refresh(family)
    return family


@router.get("/rsvp/stats", response_model=RSVPStats)
def get_stats(db: Session = Depends(get_db)):
    """Get RSVP statistics.

    Args:
        db: Database session

    Returns:
        Statistics including total guests, confirmed, declined, and pending
    """
    total = db.query(Guest).count()
    confirmed = db.query(Guest).filter(Guest.attending == True).count()
    declined = db.query(Guest).filter(Guest.attending == False).count()
    pending = db.query(Guest).filter(Guest.attending.is_(None)).count()

    return RSVPStats(
        total_guests=total,
        confirmed=confirmed,
        declined=declined,
        pending=pending,
    )
