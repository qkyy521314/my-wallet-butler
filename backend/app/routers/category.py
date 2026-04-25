from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_db
from .. import schemas, crud
from ..utils.exceptions import InsufficientPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Category])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    categories = await crud.category.get_multi(db, skip=skip, limit=limit)
    return categories


@router.get("/{category_id}", response_model=schemas.Category)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await crud.category.get(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=schemas.Category)
async def create_category(
    category: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    db_category = await crud.category.create(db, category)
    return db_category


@router.put("/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_category = await crud.category.get(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    updated_category = await crud.category.update(db, db_category, category_update)
    return updated_category


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await crud.category.get(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await crud.category.remove(db, category)
    return {"success": True, "message": "Category deleted successfully"}