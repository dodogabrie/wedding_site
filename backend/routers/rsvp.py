"""RSVP API endpoints for managing guest attendance."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from db import get_db
from models import Family, Guest, VoteAudit
from schemas import (
    GuestResponse,
    GuestUpdate,
    FamilyResponse,
    FamilyGuestsUpdate,
    RSVPStats,
)

router = APIRouter(prefix="/api", tags=["rsvp"])
MULTI_GROUP_WARNING = (
    "Perfavore, è per noi importante conoscere il numero di persone che "
    "accettano su questa pagina, comunicaci solo la tua partecipazione"
)


def _sync_legacy_attendance_fields(guest: Guest) -> None:
    """Derive legacy fields from per-event booleans."""
    ceremony = guest.attend_ceremony
    lunch = guest.attend_lunch

    if ceremony is True or lunch is True:
        guest.attending = True
    elif ceremony is False and lunch is False:
        guest.attending = False
    else:
        guest.attending = None

    # Legacy single-choice field cannot represent "both"; keep a best-effort value.
    if ceremony is False and lunch is False:
        guest.attendance_choice = "decline"
    elif ceremony is True and lunch is not True:
        guest.attendance_choice = "ceremony"
    elif lunch is True and ceremony is not True:
        guest.attendance_choice = "lunch"
    else:
        guest.attendance_choice = None


def _apply_attendance_flags(
    guest: Guest, attend_ceremony: bool | None, attend_lunch: bool | None
) -> None:
    """Apply per-event RSVP values and sync legacy compatibility fields."""
    guest.attend_ceremony = attend_ceremony
    guest.attend_lunch = attend_lunch
    _sync_legacy_attendance_fields(guest)


def _flags_from_attendance_choice(choice: str | None) -> tuple[bool | None, bool | None]:
    """Map legacy exclusive choice to per-event flags."""
    if choice is None:
        return (None, None)
    if choice == "ceremony":
        return (True, False)
    if choice == "lunch":
        return (False, True)
    if choice == "decline":
        return (False, False)
    return (None, None)


def _flags_from_legacy_attending(attending: bool | None) -> tuple[bool | None, bool | None]:
    """Map old single boolean payloads to per-event flags."""
    if attending is None:
        return (None, None)
    if attending is True:
        # Historical payloads did not distinguish event; keep ceremony as accepted
        # and lunch unresolved to avoid inventing data.
        return (True, None)
    return (False, False)


def _get_client_ip(request: Request) -> str:
    """Best-effort extraction of real client IP behind reverse proxies."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def _vote_scope_for_guest(guest: Guest) -> tuple[str, int]:
    """Group guest votes by family when present, else by single guest."""
    if guest.family_id is not None:
        return ("family", guest.family_id)
    return ("guest", guest.id)


def _attach_multi_group_warning_if_needed(
    db: Session, request: Request, response: Response, scope_type: str, scope_id: int
) -> None:
    """Set response header if same IP is voting across different groups."""
    ip_address = _get_client_ip(request)

    existing_other_scope = (
        db.query(VoteAudit.id)
        .filter(
            VoteAudit.ip_address == ip_address,
            (VoteAudit.scope_type != scope_type) | (VoteAudit.scope_id != scope_id),
        )
        .first()
    )

    if existing_other_scope:
        response.headers["X-RSVP-Warning"] = MULTI_GROUP_WARNING


def _record_vote_audit(
    db: Session, request: Request, scope_type: str, scope_id: int, guest_id: int
) -> None:
    """Persist one audit row per vote update."""
    db.add(
        VoteAudit(
            ip_address=_get_client_ip(request),
            scope_type=scope_type,
            scope_id=scope_id,
            guest_id=guest_id,
        )
    )


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
def update_guest(
    guest_id: int,
    update: GuestUpdate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
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

    updated_fields = update.model_fields_set

    attendance_fields_present = bool(
        {"attend_ceremony", "attend_lunch", "attendance_choice", "attending"} & updated_fields
    )

    if attendance_fields_present:
        scope_type, scope_id = _vote_scope_for_guest(guest)
        _attach_multi_group_warning_if_needed(
            db=db,
            request=request,
            response=response,
            scope_type=scope_type,
            scope_id=scope_id,
        )
        next_ceremony = guest.attend_ceremony
        next_lunch = guest.attend_lunch

        if "attend_ceremony" in updated_fields:
            next_ceremony = update.attend_ceremony
        if "attend_lunch" in updated_fields:
            next_lunch = update.attend_lunch

        if "attendance_choice" in updated_fields:
            next_ceremony, next_lunch = _flags_from_attendance_choice(update.attendance_choice)
        elif "attending" in updated_fields and "attend_ceremony" not in updated_fields and "attend_lunch" not in updated_fields:
            next_ceremony, next_lunch = _flags_from_legacy_attending(update.attending)

        _apply_attendance_flags(guest, next_ceremony, next_lunch)
        _record_vote_audit(
            db=db,
            request=request,
            scope_type=scope_type,
            scope_id=scope_id,
            guest_id=guest.id,
        )
    if "allergens" in updated_fields:
        guest.allergens = update.allergens or []
    if "dietary_notes" in updated_fields:
        guest.dietary_notes = update.dietary_notes

    db.commit()
    db.refresh(guest)
    return guest


@router.patch("/families/{family_id}/guests", response_model=FamilyResponse)
def update_family_guests(
    family_id: int,
    update: FamilyGuestsUpdate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
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

    _attach_multi_group_warning_if_needed(
        db=db,
        request=request,
        response=response,
        scope_type="family",
        scope_id=family_id,
    )

    for guest_id, attendance_value in update.guest_updates.items():
        guest = db.query(Guest).filter(
            Guest.id == guest_id, Guest.family_id == family_id
        ).first()
        if guest:
            if isinstance(attendance_value, str) or attendance_value is None:
                ceremony, lunch = _flags_from_attendance_choice(attendance_value)
                _apply_attendance_flags(guest, ceremony, lunch)
            else:
                ceremony, lunch = _flags_from_legacy_attending(attendance_value)
                _apply_attendance_flags(guest, ceremony, lunch)
            _record_vote_audit(
                db=db,
                request=request,
                scope_type="family",
                scope_id=family_id,
                guest_id=guest.id,
            )

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
