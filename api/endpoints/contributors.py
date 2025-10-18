"""Contributor endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid

from api.core.database import get_db, Contributor
from api.schemas.books import ContributorCreate, ContributorResponse

router = APIRouter()


@router.post("/contributors", response_model=ContributorResponse, status_code=status.HTTP_201_CREATED)
async def create_contributor(contributor_data: ContributorCreate, db: Session = Depends(get_db)):
    """Create a new contributor."""
    contributor = Contributor(
        id=str(uuid.uuid4()),
        full_name=contributor_data.full_name
    )
    
    db.add(contributor)
    db.commit()
    db.refresh(contributor)
    return contributor


@router.get("/contributors", response_model=List[ContributorResponse])
async def get_contributors(db: Session = Depends(get_db)):
    """Get all contributors."""
    contributors = db.query(Contributor).all()
    return contributors


@router.get("/contributors/{contributor_id}", response_model=ContributorResponse)
async def get_contributor(contributor_id: str, db: Session = Depends(get_db)):
    """Get a specific contributor by ID."""
    contributor = db.query(Contributor).filter(Contributor.id == contributor_id).first()
    if not contributor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor not found"
        )
    return contributor