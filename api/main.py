"""Main FastAPI application."""
from fastapi import FastAPI
from api.core.database import engine, Base
from api.endpoints.books import router as books_router
from api.endpoints.contributors import router as contributors_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Database API",
    description="API for managing books, genres and contributors",
    version="0.1.0"
)

# Include routers
app.include_router(books_router, prefix="/api/v1", tags=["books"])
app.include_router(contributors_router, prefix="/api/v1", tags=["contributors"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Book Database API"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}