"""Pydantic schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator

ATTENDANCE_CHOICES = {"ceremony", "lunch", "decline"}
ALLERGEN_OPTIONS = {
    "glutine",
    "lattosio",
    "uova",
    "arachidi",
    "frutta_a_guscio",
    "soia",
    "sesamo",
    "pesce",
    "crostacei",
    "molluschi",
    "senape",
    "sedano",
    "solfiti",
}


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
    attendance_choice: str | None = None
    attend_ceremony: bool | None = None
    attend_lunch: bool | None = None
    allergens: list[str] | None = None
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
    attendance_choice: str | None = None
    attend_ceremony: bool | None = None
    attend_lunch: bool | None = None
    allergens: list[str] | None = Field(default=None)
    dietary_notes: str | None = None

    @field_validator("attendance_choice")
    @classmethod
    def validate_attendance_choice(cls, value: str | None):
        if value is None:
            return value
        if value not in ATTENDANCE_CHOICES:
            raise ValueError("Invalid attendance_choice")
        return value

    @field_validator("allergens")
    @classmethod
    def validate_allergens(cls, value: list[str] | None):
        if value is None:
            return value
        normalized = []
        for item in value:
            if item not in ALLERGEN_OPTIONS:
                raise ValueError(f"Invalid allergen option: {item}")
            if item not in normalized:
                normalized.append(item)
        return normalized


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
    guest_updates: dict[int, bool | str | None]


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
