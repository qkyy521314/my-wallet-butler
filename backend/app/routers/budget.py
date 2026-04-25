from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from ..database import get_db
from .. import schemas, crud
from ..utils.exceptions import InsufficientPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Budget])
async def get_budgets(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    year: int = Query(None, description="Year filter"),
    month: int = Query(None, description="Month filter")
):
    if year and month:
        # 按年月过滤预算
        budgets = await crud.budget.get_monthly_budgets(db, 1, year, month)  # 假设用户ID为1进行测试
    else:
        budgets = await crud.budget.get_multi(db, skip=skip, limit=limit)

    # 更新每个预算的花费金额
    for budget in budgets:
        await crud.budget.update_budget_spent_amount(db, budget.id)

    return budgets


@router.get("/{budget_id}", response_model=schemas.Budget)
async def get_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    budget = await crud.budget.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # 更新预算的花费金额
    budget = await crud.budget.update_budget_spent_amount(db, budget_id)
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

    # 更新预算的花费金额
    updated_budget = await crud.budget.update_budget_spent_amount(db, budget_id)
    return updated_budget


@router.delete("/{budget_id}")
async def delete_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    budget = await crud.budget.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    await crud.budget.remove(db, budget_id)
    return {"success": True, "message": "Budget deleted successfully"}


@router.get("/{budget_id}/stats", response_model=dict)
async def get_budget_stats(budget_id: int, db: AsyncSession = Depends(get_db)):
    """获取预算统计信息"""
    budget = await crud.budget.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    budget = await crud.budget.update_budget_spent_amount(db, budget_id)

    stats = {
        "id": budget.id,
        "name": budget.name,
        "total_amount": budget.amount,
        "spent_amount": budget.spent_amount,
        "remaining_amount": budget.amount - budget.spent_amount,
        "spent_percentage": budget.spent_percentage,
        "is_over_spent": budget.is_over_spent,
        "category_id": budget.category_id,
        "period_start": budget.period_start,
        "period_end": budget.period_end
    }

    return stats