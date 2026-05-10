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
@router.get("")
async def get_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    account_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    skip = (page - 1) * size

    accounts, total = await crud.account.get_multi(
        db,
        skip=skip,
        limit=size,
        user_id=current_user.id,
        account_type=account_type,
        is_active=is_active
    )

    total_pages = (total + size - 1) // size  # 向上取整

    # Convert SQLAlchemy models to dicts
    items = [schemas.AccountInDB.model_validate(a).model_dump() for a in accounts]

    paginated_data = {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }

    return SuccessResponse(code=200, message="Accounts retrieved successfully", data=paginated_data)


@router.get("/{account_id}")
async def get_account(account_id: int,
                     db: AsyncSession = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):
    account = await crud.account.get(db, account_id, user_id=current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or insufficient permissions")
    account_out = schemas.AccountInDB.model_validate(account)
    return SuccessResponse(code=200, message="Account retrieved successfully", data=account_out.model_dump())


@router.post("/")
@router.post("")
async def create_account(
    account: schemas.AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_account = await crud.account.create(db, account, user_id=current_user.id)
    account_out = schemas.AccountInDB.model_validate(db_account)
    return SuccessResponse(code=200, message="Account created successfully", data=account_out.model_dump())


@router.put("/{account_id}")
async def update_account(
    account_id: int,
    account_update: schemas.AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_account = await crud.account.get(db, account_id, user_id=current_user.id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found or insufficient permissions")

    updated_account = await crud.account.update(db, db_obj=db_account, obj_in=account_update)
    account_out = schemas.AccountInDB.model_validate(updated_account)
    return SuccessResponse(code=200, message="Account updated successfully", data=account_out.model_dump())


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    account = await crud.account.get(db, account_id, user_id=current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or insufficient permissions")

    await crud.account.remove(db, account_id, user_id=current_user.id)
    return SuccessResponse(code=200, message="Account deleted successfully", data=None)