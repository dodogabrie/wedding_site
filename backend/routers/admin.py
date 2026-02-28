"""Admin API endpoints for managing the guest list and families."""

import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from db import get_db
from models import Family, Guest
from routers.rsvp import _apply_attendance_flags
from schemas import (
    AdminDataResponse,
    AdminGuestResponse,
    AdminGuestUpdate,
    AdminFamilyResponse,
    AdminFamilyUpdate,
    FamilyBase,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Get admin password from environment or use a default for development
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "WeddingManagement2026!")


async def verify_admin(x_admin_password: Annotated[str | None, Header()] = None):
    """Dependency to verify the admin password from headers."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password",
        )
    return True


@router.get("/data", response_model=AdminDataResponse)
def get_admin_data(
    admin: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all families and individual guests with full details."""
    families = db.query(Family).all()
    individuals = db.query(Guest).filter(Guest.family_id.is_(None)).all()
    return {
        "families": families,
        "individuals": individuals
    }


@router.patch("/guests/{guest_id}", response_model=AdminGuestResponse)
def admin_update_guest(
    guest_id: int,
    update: AdminGuestUpdate,
    admin: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Administratively update a guest's details."""
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    updated_fields = update.model_dump(exclude_unset=True)
    
    # Handle family_id specifically to ensure it's valid if provided
    if "family_id" in updated_fields and updated_fields["family_id"] is not None:
        family = db.query(Family).filter(Family.id == updated_fields["family_id"]).first()
        if not family:
            raise HTTPException(status_code=400, detail="Target family not found")

    # Handle attendance sync using the shared logic from rsvp router
    if "attend_ceremony" in updated_fields or "attend_lunch" in updated_fields:
        next_ceremony = updated_fields.get("attend_ceremony", guest.attend_ceremony)
        next_lunch = updated_fields.get("attend_lunch", guest.attend_lunch)
        _apply_attendance_flags(guest, next_ceremony, next_lunch)
        
        # Remove from updated_fields to avoid redundant setattr below
        updated_fields.pop("attend_ceremony", None)
        updated_fields.pop("attend_lunch", None)
        # Also pop legacy 'attending' if present in update, as _apply_attendance_flags handles it
        updated_fields.pop("attending", None)

    for field, value in updated_fields.items():
        setattr(guest, field, value)

    db.commit()
    db.refresh(guest)
    return guest


@router.post("/guests", response_model=AdminGuestResponse, status_code=status.HTTP_201_CREATED)
def admin_create_guest(
    guest_data: AdminGuestUpdate,
    admin: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new guest."""
    if not guest_data.name:
        raise HTTPException(status_code=400, detail="Guest name is required")
        
    guest_dict = guest_data.model_dump(exclude_unset=True)
    new_guest = Guest(name=guest_dict.pop("name"))
    
    # If attendance is provided, apply it via the sync logic
    if "attend_ceremony" in guest_dict or "attend_lunch" in guest_dict:
        ceremony = guest_dict.pop("attend_ceremony", None)
        lunch = guest_dict.pop("attend_lunch", None)
        _apply_attendance_flags(new_guest, ceremony, lunch)
        guest_dict.pop("attending", None)

    for field, value in guest_dict.items():
        setattr(new_guest, field, value)

    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)
    return new_guest


@router.delete("/guests/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_guest(
    guest_id: int,
    admin: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Remove a guest from the list."""
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    db.delete(guest)
    db.commit()
    return None


@router.post("/families", response_model=AdminFamilyResponse, status_code=status.HTTP_201_CREATED)
def admin_create_family(
    family_data: FamilyBase,
    admin: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new family group."""
    new_family = Family(family_name=family_data.family_name)
    db.add(new_family)
    db.commit()
    db.refresh(new_family)
    return new_family


@router.patch("/families/{family_id}", response_model=AdminFamilyResponse)
def admin_update_family(
    family_id: int,
    update: AdminFamilyUpdate,
    admin: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update family details (e.g. rename)."""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    if update.family_name:
        family.family_name = update.family_name

    db.commit()
    db.refresh(family)
    return family


@router.delete("/families/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_family(
    family_id: int,
    admin: bool = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete a family group. Members are NOT deleted but become individual guests."""
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    # Dissociate members
    db.query(Guest).filter(Guest.family_id == family_id).update({"family_id": None})
    
    db.delete(family)
    db.commit()
    return None
