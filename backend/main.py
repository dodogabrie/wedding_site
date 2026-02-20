"""FastAPI application entry point for the wedding website backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import engine, Base
from routers import rsvp

# Create database tables
Base.metadata.create_all(bind=engine)

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
