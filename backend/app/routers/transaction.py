from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..database import get_db
from .. import schemas, crud, models
from ..utils.exceptions import InsufficientPermissions
from ..services.auth import get_current_user
from ..schemas.common import SuccessResponse, PaginatedResponse
from sqlalchemy import func
from pydantic import BaseModel


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    description: Optional[str] = ""
    category_id: Optional[int] = None
    date: Optional[str] = None
    is_active: Optional[bool] = True


router = APIRouter()


@router.get("")
@router.get("/")
async def get_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    transaction_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    account_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    skip = (page - 1) * size

    transactions, total = await crud.transaction.get_multi(
        db,
        skip=skip,
        limit=size,
        user_id=current_user.id,
        transaction_type=transaction_type,
        is_active=is_active,
        account_id=account_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date
    )

    total_pages = (total + size - 1) // size  # 向上取整

    items = [schemas.TransactionInDB.model_validate(t).model_dump() for t in transactions]

    paginated_data = {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }

    return SuccessResponse(code=200, message="Transactions retrieved successfully", data=paginated_data)


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transaction = await crud.transaction.get(db, transaction_id, user_id=current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or insufficient permissions")
    transaction_out = schemas.TransactionInDB.model_validate(transaction)
    return SuccessResponse(code=200, message="Transaction retrieved successfully", data=transaction_out.model_dump())


@router.post("/")
@router.post("")
async def create_transaction(
    transaction: schemas.TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_transaction = await crud.transaction.create(db, transaction, user_id=current_user.id)
    transaction_out = schemas.TransactionInDB.model_validate(db_transaction)
    return SuccessResponse(code=200, message="Transaction created successfully", data=transaction_out.model_dump())


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_transaction = await crud.transaction.get(db, transaction_id, user_id=current_user.id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or insufficient permissions")

    updated_transaction = await crud.transaction.update(db, db_obj=db_transaction, obj_in=transaction_update)
    transaction_out = schemas.TransactionInDB.model_validate(updated_transaction)
    return SuccessResponse(code=200, message="Transaction updated successfully", data=transaction_out.model_dump())


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transaction = await crud.transaction.get(db, transaction_id, user_id=current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or insufficient permissions")

    await crud.transaction.remove(db, transaction_id, obj=transaction)
    return SuccessResponse(code=200, message="Transaction deleted successfully", data=None)


@router.post("/transfer/")
async def create_transfer(
    transfer_request: TransferRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        transfer_data = {
            'from_account_id': transfer_request.from_account_id,
            'to_account_id': transfer_request.to_account_id,
            'amount': transfer_request.amount,
            'description': transfer_request.description,
            'category_id': transfer_request.category_id,
            'date': transfer_request.date,
            'is_active': transfer_request.is_active
        }

        transfer = await crud.transaction.create_transfer(db, transfer_data, current_user.id)
        return SuccessResponse(code=200, message="Transfer completed successfully", data=transfer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))