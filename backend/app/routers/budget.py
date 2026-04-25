from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_db
from .. import schemas, crud
from ..utils.exceptions import InsufficientPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Budget])
async def get_budgets(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    budgets = await crud.budget.get_multi(db, skip=skip, limit=limit)
    return budgets


@router.get("/{budget_id}", response_model=schemas.Budget)
async def get_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    budget = await crud.budget.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.post("/", response_model=schemas.Budget)
async def create_budget(
    budget: schemas.BudgetCreate,
    db: AsyncSession = Depends(get_db)
):
    db_budget = await crud.budget.create(db, budget)
    return db_budget


@router.put("/{budget_id}", response_model=schemas.Budget)
async def update_budget(
    budget_id: int,
    budget_update: schemas.BudgetUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_budget = await crud.budget.get(db, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    updated_budget = await crud.budget.update(db, db_budget, budget_update)
    return updated_budget


@router.delete("/{budget_id}")
async def delete_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    budget = await crud.budget.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    await crud.budget.remove(db, budget)
    return {"success": True, "message": "Budget deleted successfully"}