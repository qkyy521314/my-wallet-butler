from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from ..database import get_db
from .. import schemas, crud, models
from ..utils.exceptions import InsufficientPermissions
from ..services.auth import get_current_user
from ..schemas.common import SuccessResponse

router = APIRouter()


@router.get("")
@router.get("/")
async def get_budgets(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    year: int = Query(None, description="Year filter"),
    month: int = Query(None, description="Month filter")
):
    if year and month:
        # 按年月过滤预算
        budgets = await crud.budget.get_monthly_budgets(db, current_user.id, year, month)
    else:
        budgets = await crud.budget.get_multi(db, skip=skip, limit=limit, user_id=current_user.id)

    # 更新每个预算的花费金额
    for budget in budgets:
        await crud.budget.update_budget_spent_amount(db, budget.id)

    items = [schemas.Budget.model_validate(b).model_dump() for b in budgets]
    return SuccessResponse(code=200, message="Budgets retrieved successfully", data={"items": items, "total": len(items)})


@router.get("/{budget_id}")
async def get_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    budget = await crud.budget.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # 更新预算的花费金额
    budget = await crud.budget.update_budget_spent_amount(db, budget_id)
    budget_out = schemas.Budget.model_validate(budget)
    return SuccessResponse(code=200, message="Budget retrieved successfully", data=budget_out.model_dump())


@router.post("/")
@router.post("")
async def create_budget(
    budget: schemas.BudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_budget = await crud.budget.create(db, budget, user_id=current_user.id)
    budget_out = schemas.Budget.model_validate(db_budget)
    return SuccessResponse(code=200, message="Budget created successfully", data=budget_out.model_dump())


@router.put("/{budget_id}")
async def update_budget(
    budget_id: int,
    budget_update: schemas.BudgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_budget = await crud.budget.get(db, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    updated_budget = await crud.budget.update(db, db_budget, budget_update)

    # 更新预算的花费金额
    updated_budget = await crud.budget.update_budget_spent_amount(db, budget_id)
    budget_out = schemas.Budget.model_validate(updated_budget)
    return SuccessResponse(code=200, message="Budget updated successfully", data=budget_out.model_dump())


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    budget = await crud.budget.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    await crud.budget.remove(db, budget_id)
    return SuccessResponse(code=200, message="Budget deleted successfully", data=None)


@router.get("/{budget_id}/stats")
async def get_budget_stats(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
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

    return SuccessResponse(code=200, message="Budget stats retrieved successfully", data=stats)
