"""SQLAlchemy database models for the wedding RSVP system."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
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
        dietary_notes: Optional dietary restrictions or notes
        updated_at: Last time the RSVP was updated
        family: Relationship to the Family model
    """
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    attending = Column(Boolean, nullable=True, default=None)
    dietary_notes = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    family = relationship("Family", back_populates="guests")


class VoteAudit(Base):
    """Tracks RSVP updates by client IP to detect multi-group voting."""
    __tablename__ = "vote_audits"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, nullable=False, index=True)
    scope_type = Column(String, nullable=False)  # "family" or "guest"
    scope_id = Column(Integer, nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
