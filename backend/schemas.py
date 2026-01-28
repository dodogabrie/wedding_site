"""Pydantic schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel


class GuestBase(BaseModel):
    """Base schema for guest data."""
    name: str


class GuestResponse(GuestBase):
    """Schema for guest responses.

    Attributes:
        id: Guest ID
        name: Guest's full name
        family_id: ID of associated family (if any)
        attending: Attendance status (True/False/None)
        dietary_notes: Optional dietary notes
        updated_at: Last update timestamp
    """
    id: int
    family_id: int | None
    attending: bool | None
    dietary_notes: str | None
    updated_at: datetime

    class Config:
        from_attributes = True


class GuestUpdate(BaseModel):
    """Schema for updating a guest's RSVP.

    Attributes:
        attending: New attendance status
        dietary_notes: Optional dietary notes
    """
    attending: bool | None = None
    dietary_notes: str | None = None


class FamilyBase(BaseModel):
    """Base schema for family data."""
    family_name: str


class FamilyResponse(FamilyBase):
    """Schema for family responses with nested guests.

    Attributes:
        id: Family ID
        family_name: Display name for the family
        guests: List of guests in this family
    """
    id: int
    guests: list[GuestResponse]

    class Config:
        from_attributes = True


class FamilyGuestsUpdate(BaseModel):
    """Schema for bulk updating family members' attendance.

    Attributes:
        guest_updates: Dict mapping guest_id to attendance status
    """
    guest_updates: dict[int, bool | None]


class RSVPStats(BaseModel):
    """Schema for RSVP statistics.

    Attributes:
        total_guests: Total number of guests
        confirmed: Number of guests confirmed attending
        declined: Number of guests who declined
        pending: Number of guests who haven't responded
    """
    total_guests: int
    confirmed: int
    declined: int
    pending: int
