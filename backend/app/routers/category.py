from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..database import get_db
from .. import schemas, crud, models
from ..utils.exceptions import InsufficientPermissions
from ..services.auth import get_current_user
from ..schemas.common import SuccessResponse, PaginatedResponse
from sqlalchemy import func


router = APIRouter()


@router.get("/")
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    parent_id: Optional[int] = Query(None),
    tree: bool = Query(False, description="Return category tree structure")
):
    if tree:
        # 返回树形结构
        category_tree = await crud.category.get_tree(db, user_id=current_user.id, category_type=category_type)
        return SuccessResponse(code=200, message="Category tree retrieved successfully", data=category_tree)
    else:
        skip = (page - 1) * size

        categories, total = await crud.category.get_multi(
            db,
            skip=skip,
            limit=size,
            user_id=current_user.id,
            category_type=category_type,
            is_active=is_active,
            parent_id=parent_id
        )

        total_pages = (total + size - 1) // size  # 向上取整

        paginated_data = {
            "items": categories,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages
        }

        return SuccessResponse(code=200, message="Categories retrieved successfully", data=paginated_data)


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    category = await crud.category.get(db, category_id, user_id=current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found or insufficient permissions")
    return SuccessResponse(code=200, message="Category retrieved successfully", data=category)


@router.post("/")
async def create_category(
    category: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_category = await crud.category.create(db, category, user_id=current_user.id)
    return SuccessResponse(code=200, message="Category created successfully", data=db_category)


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_category = await crud.category.get(db, category_id, user_id=current_user.id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found or insufficient permissions")

    updated_category = await crud.category.update(db, db_obj=db_category, obj_in=category_update)
    return SuccessResponse(code=200, message="Category updated successfully", data=updated_category)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    category = await crud.category.get(db, category_id, user_id=current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found or insufficient permissions")

    await crud.category.remove(db, category_id, user_id=current_user.id)
    return SuccessResponse(code=200, message="Category deleted successfully", data=None)