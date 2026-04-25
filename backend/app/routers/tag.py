from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_db
from .. import schemas, crud
from ..utils.exceptions import InsufficientPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Tag])
async def get_tags(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    tags = await crud.tag.get_multi(db, skip=skip, limit=limit)
    return tags


@router.get("/{tag_id}", response_model=schemas.Tag)
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await crud.tag.get(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/", response_model=schemas.Tag)
async def create_tag(
    tag: schemas.TagCreate,
    db: AsyncSession = Depends(get_db)
):
    db_tag = await crud.tag.create(db, tag)
    return db_tag


@router.put("/{tag_id}", response_model=schemas.Tag)
async def update_tag(
    tag_id: int,
    tag_update: schemas.TagUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_tag = await crud.tag.get(db, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    updated_tag = await crud.tag.update(db, db_tag, tag_update)
    return updated_tag


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await crud.tag.get(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await crud.tag.remove(db, tag)
    return {"success": True, "message": "Tag deleted successfully"}