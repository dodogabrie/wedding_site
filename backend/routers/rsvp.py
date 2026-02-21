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

    if update.attending is not None:
        scope_type, scope_id = _vote_scope_for_guest(guest)
        _attach_multi_group_warning_if_needed(
            db=db,
            request=request,
            response=response,
            scope_type=scope_type,
            scope_id=scope_id,
        )
        guest.attending = update.attending
        _record_vote_audit(
            db=db,
            request=request,
            scope_type=scope_type,
            scope_id=scope_id,
            guest_id=guest.id,
        )
    if update.dietary_notes is not None:
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

    for guest_id, attending in update.guest_updates.items():
        guest = db.query(Guest).filter(
            Guest.id == guest_id, Guest.family_id == family_id
        ).first()
        if guest:
            guest.attending = attending
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
