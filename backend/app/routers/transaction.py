from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_db
from .. import schemas, crud
from ..utils.exceptions import InsufficientPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Transaction])
async def get_transactions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    transactions = await crud.transaction.get_multi(db, skip=skip, limit=limit)
    return transactions


@router.get("/{transaction_id}", response_model=schemas.Transaction)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    transaction = await crud.transaction.get(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("/", response_model=schemas.Transaction)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    db_transaction = await crud.transaction.create(db, transaction)
    return db_transaction


@router.put("/{transaction_id}", response_model=schemas.Transaction)
async def update_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_transaction = await crud.transaction.get(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updated_transaction = await crud.transaction.update(db, db_transaction, transaction_update)
    return updated_transaction


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    transaction = await crud.transaction.get(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await crud.transaction.remove(db, transaction)
    return {"success": True, "message": "Transaction deleted successfully"}