"""仪表盘相关路由"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget
from app.models.account import Account
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter()


def _get_user_id(current_user: User) -> int:
    return current_user.id


# ============================================================
# 仪表盘概览
# ============================================================

@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """仪表盘统计摘要（总资产、本月收入、本月支出、结余）"""
    user_id = _get_user_id(current_user)

    # 本月日期范围
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_of_month = now.replace(day=now.day, hour=23, minute=59, second=59, microsecond=999999)

    # 本月收入
    income_stmt = select(func.sum(Transaction.amount)).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "income",
            Transaction.date >= first_day_of_month,
            Transaction.date <= last_day_of_month,
            Transaction.is_active == True,
        )
    )
    income_result = await db.execute(income_stmt)
    monthly_income = float(income_result.scalar() or 0)

    # 本月支出
    expense_stmt = select(func.sum(Transaction.amount)).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.date >= first_day_of_month,
            Transaction.date <= last_day_of_month,
            Transaction.is_active == True,
        )
    )
    expense_result = await db.execute(expense_stmt)
    monthly_expense = float(expense_result.scalar() or 0)

    # 总资产（所有账户余额之和）
    accounts_stmt = select(func.sum(Account.balance)).where(
        and_(
            Account.user_id == user_id,
            Account.is_active == True,
        )
    )
    accounts_result = await db.execute(accounts_stmt)
    total_assets = float(accounts_result.scalar() or 0)

    # 本月结余
    balance = monthly_income - monthly_expense

    return {
        "total_assets": total_assets,
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "balance": balance,
    }


# ============================================================
# 最近交易
# ============================================================

@router.get("/recent-transactions")
async def get_recent_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 5,
):
    """获取最近交易记录"""
    user_id = _get_user_id(current_user)

    stmt = (
        select(
            Transaction.id,
            Transaction.description,
            Transaction.amount,
            Transaction.date,
            Category.name.label("category_name"),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user_id,
            Transaction.is_active == True,
        )
        .order_by(Transaction.date.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    transactions = []
    for row in result.fetchall():
        transactions.append({
            "id": row[0],
            "description": row[1],
            "amount": float(row[2]),
            "date": row[3].isoformat() if row[3] else None,
            "category": {"name": row[4] or "未分类"},
        })

    return {"transactions": transactions}


# ============================================================
# 账户余额
# ============================================================

@router.get("/account-balances")
async def get_account_balances(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取所有账户余额"""
    user_id = _get_user_id(current_user)

    stmt = select(Account).where(
        and_(
            Account.user_id == user_id,
            Account.is_active == True,
        )
    ).order_by(Account.name)

    result = await db.execute(stmt)
    accounts = []
    for account in result.scalars().all():
        accounts.append({
            "id": account.id,
            "name": account.name,
            "type": account.account_type,
            "balance": float(account.balance),
        })

    return {"accounts": accounts}


# ============================================================
# 预算概览
# ============================================================

@router.get("/budget-overview")
async def get_budget_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取本月预算执行概览"""
    user_id = _get_user_id(current_user)

    # 本月日期范围
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_of_month = now.replace(day=now.day, hour=23, minute=59, second=59, microsecond=999999)

    # 获取本月预算（预加载 category 关联）
    budgets_stmt = select(Budget).options(
        joinedload(Budget.category)
    ).where(
        and_(
            Budget.user_id == user_id,
            Budget.is_active == True,
            Budget.period_start <= last_day_of_month,
            Budget.period_end >= first_day_of_month,
        )
    )

    result = await db.execute(budgets_stmt)
    budgets = result.scalars().all()

    budget_overview = []
    for budget in budgets:
        # 计算已花费金额
        spent_stmt = select(func.sum(Transaction.amount)).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.category_id == budget.category_id,
                Transaction.transaction_type == "expense",
                Transaction.date >= first_day_of_month,
                Transaction.date <= last_day_of_month,
                Transaction.is_active == True,
            )
        )
        spent_result = await db.execute(spent_stmt)
        spent = float(spent_result.scalar() or 0)

        # 计算百分比
        budget_amount = float(budget.amount)
        percent = round((spent / budget_amount * 100) if budget_amount > 0 else 0, 2)

        budget_overview.append({
            "category": budget.category.name if budget.category else "未分类",
            "spent": spent,
            "limit": budget_amount,
            "percent": percent,
        })

    return {"budgets": budget_overview}
