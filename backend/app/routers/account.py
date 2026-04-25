from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_db
from .. import schemas, crud
from ..utils.exceptions import InsufficientPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Account])
async def get_accounts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    accounts = await crud.account.get_multi(db, skip=skip, limit=limit)
    return accounts


@router.get("/{account_id}", response_model=schemas.Account)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await crud.account.get(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/", response_model=schemas.Account)
async def create_account(
    account: schemas.AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    db_account = await crud.account.create(db, account)
    return db_account


@router.put("/{account_id}", response_model=schemas.Account)
async def update_account(
    account_id: int,
    account_update: schemas.AccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_account = await crud.account.get(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    updated_account = await crud.account.update(db, db_account, account_update)
    return updated_account


@router.delete("/{account_id}")
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await crud.account.get(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    await crud.account.remove(db, account)
    return {"success": True, "message": "Account deleted successfully"}