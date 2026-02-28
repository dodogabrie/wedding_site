"""SQLAlchemy database models for the wedding RSVP system."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from db import Base


class Family(Base):
    """Represents a family group for RSVP purposes.

    Attributes:
        id: Primary key
        family_name: Display name for the family
        created_at: Timestamp when the family was added
        guests: List of guests belonging to this family
    """
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    family_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    guests = relationship("Guest", back_populates="family")


class Guest(Base):
    """Represents an individual guest.

    Attributes:
        id: Primary key
        name: Guest's full name
        family_id: Foreign key to family (nullable for individual guests)
        attending: True=attending, False=not attending, None=not responded
        attendance_choice: Legacy 3-state RSVP response (kept for compatibility)
        attend_ceremony: Per-event RSVP for ceremony
        attend_lunch: Per-event RSVP for lunch
        allergens: Optional list of allergens/intolerances selected by the guest
        dietary_notes: Optional dietary restrictions or notes (legacy free text)
        updated_at: Last time the RSVP was updated
        family: Relationship to the Family model
    """
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    attending = Column(Boolean, nullable=True, default=None)
    attendance_choice = Column(String, nullable=True, default=None)
    attend_ceremony = Column(Boolean, nullable=True, default=None)
    attend_lunch = Column(Boolean, nullable=True, default=None)
    allergens = Column(JSON, nullable=True, default=list)
    dietary_notes = Column(String, nullable=True)
    admin_notes = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    family = relationship("Family", back_populates="guests")


class Photo(Base):
    """Represents a photo uploaded to the wedding gallery.

    Attributes:
        id: UUID4 hex used as filename
        original_filename: Name of the file as uploaded
        uploader_name: Optional name of the person who uploaded
        caption: Optional caption for the photo
        mime_type: MIME type of the original upload
        file_size: Size of the processed file in bytes
        width: Width of the processed image in pixels
        height: Height of the processed image in pixels
        created_at: Timestamp when the photo was uploaded
    """
    __tablename__ = "photos"

    id = Column(String, primary_key=True)
    original_filename = Column(String, nullable=False)
    uploader_name = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class VoteAudit(Base):
    """Tracks RSVP updates by client IP to detect multi-group voting."""
    __tablename__ = "vote_audits"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, nullable=False, index=True)
    scope_type = Column(String, nullable=False)  # "family" or "guest"
    scope_id = Column(Integer, nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
