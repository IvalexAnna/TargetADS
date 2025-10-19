from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid

from api.core.database import get_db, Contributor
from api.schemas.books import ContributorCreate, ContributorBase

router = APIRouter()


@router.post("/contributors", response_model=ContributorBase, status_code=status.HTTP_201_CREATED)
async def create_contributor(contributor_data: ContributorCreate, db: Session = Depends(get_db)):
    """Создает нового контрибьютора в системе.
    
    Args:
        contributor_data: Данные для создания контрибьютора
        db: Сессия базы данных
        
    Returns:
        ContributorBase: Созданный контрибьютор
        
    Raises:
        HTTPException: Если произошла ошибка при создании
    """
    contributor = Contributor(
        id=str(uuid.uuid4()),
        full_name=contributor_data.full_name
    )
    
    db.add(contributor)
    db.commit()
    db.refresh(contributor)
    return contributor


@router.get("/contributors", response_model=List[ContributorBase])
async def get_contributors(db: Session = Depends(get_db)):
    """Возвращает список всех контрибьюторов.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[ContributorBase]: Список всех контрибьюторов
    """
    contributors = db.query(Contributor).all()
    return contributors


@router.get("/contributors/{contributor_id}", response_model=ContributorBase)
async def get_contributor(contributor_id: str, db: Session = Depends(get_db)):
    """Возвращает контрибьютора по указанному идентификатору.
    
    Args:
        contributor_id: UUID контрибьютора
        db: Сессия базы данных
        
    Returns:
        ContributorBase: Найденный контрибьютор
        
    Raises:
        HTTPException: 404 если контрибьютор не найден
    """
    contributor = db.query(Contributor).filter(Contributor.id == contributor_id).first()
    if not contributor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor not found"
        )
    return contributor