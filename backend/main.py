"""FastAPI application entry point for the wedding website backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from db import engine, Base
from routers import rsvp

# Create database tables
Base.metadata.create_all(bind=engine)


def ensure_guest_columns():
    """Add backward-compatible columns to existing SQLite DBs."""
    inspector = inspect(engine)
    if "guests" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("guests")}
    statements = []

    if "attendance_choice" not in existing_columns:
        statements.append("ALTER TABLE guests ADD COLUMN attendance_choice VARCHAR")
    if "attend_ceremony" not in existing_columns:
        statements.append("ALTER TABLE guests ADD COLUMN attend_ceremony BOOLEAN")
    if "attend_lunch" not in existing_columns:
        statements.append("ALTER TABLE guests ADD COLUMN attend_lunch BOOLEAN")
    if "allergens" not in existing_columns:
        # JSON payload is serialized in SQLite as text.
        statements.append("ALTER TABLE guests ADD COLUMN allergens TEXT")

    if not statements:
        return

    with engine.begin() as connection:
        for stmt in statements:
            connection.execute(text(stmt))


ensure_guest_columns()

app = FastAPI(title="Wedding RSVP API", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "https://caterina.edoardogabrielli.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rsvp.router)


@app.get("/")
def root():
    """Health check endpoint.

    Returns:
        Status message
    """
    return {"status": "ok", "message": "Wedding RSVP API"}
