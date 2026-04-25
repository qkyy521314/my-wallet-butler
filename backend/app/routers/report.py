from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, extract
from typing import List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from ..database import get_db
from .. import crud
from ..models.transaction import Transaction
from ..models.category import Category
from ..models.budget import Budget
from sqlalchemy import select

router = APIRouter()


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    start_date: datetime = Query(..., description="Start date for the summary"),
    end_date: datetime = Query(..., description="End date for the summary"),
    user_id: int = Query(..., description="User ID")
):
    """收支概览统计（总收入、总支出、净收入）"""
    # 获取收入总额
    income_stmt = select(func.sum(Transaction.amount)).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'income',
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.is_active == True
        )
    )
    income_result = await db.execute(income_stmt)
    total_income = income_result.scalar() or 0

    # 获取支出总额
    expense_stmt = select(func.sum(Transaction.amount)).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.is_active == True
        )
    )
    expense_result = await db.execute(expense_stmt)
    total_expense = expense_result.scalar() or 0

    # 计算净收入
    net_income = total_income - total_expense

    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "net_income": float(net_income),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }


@router.get("/category-analysis")
async def get_category_analysis(
    db: AsyncSession = Depends(get_db),
    start_date: datetime = Query(..., description="Start date for the analysis"),
    end_date: datetime = Query(..., description="End date for the analysis"),
    user_id: int = Query(..., description="User ID"),
    transaction_type: str = Query("expense", description="Type of transaction (income/expense)")
):
    """分类支出占比（饼图数据）"""
    # 获取指定类型交易的分类统计
    stmt = select(
        func.sum(Transaction.amount).label('total'),
        Transaction.category_id,
        Category.name.label('category_name')
    ).select_from(
        Transaction.__table__.join(Category.__table__)
    ).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.is_active == True,
            Transaction.category_id == Category.id
        )
    ).group_by(Transaction.category_id, Category.name)

    result = await db.execute(stmt)
    rows = result.fetchall()

    total_amount = sum(float(row[0] or 0) for row in rows)

    category_data = []
    for row in rows:
        total = float(row[0] or 0)
        category_id = row[1]
        category_name = row[2]

        percentage = round((total / total_amount * 100) if total_amount > 0 else 0, 2)
        category_data.append({
            "category_id": category_id,
            "category_name": category_name,
            "amount": total,
            "percentage": percentage
        })

    return {
        "total_amount": total_amount,
        "categories": category_data,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "transaction_type": transaction_type
    }


@router.get("/trend-analysis")
async def get_trend_analysis(
    db: AsyncSession = Depends(get_db),
    start_date: datetime = Query(..., description="Start date for the analysis"),
    end_date: datetime = Query(..., description="End date for the analysis"),
    user_id: int = Query(..., description="User ID"),
    group_by: str = Query("day", description="Group by (day, week, month)")
):
    """收支趋势（折线图数据）"""
    # 构建收入趋势查询
    income_stmt = select(
        func.to_char(Transaction.date, 'YYYY-MM-DD' if group_by == 'day' else 'YYYY-MM').label('date_group'),
        func.sum(Transaction.amount).label('total')
    ).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'income',
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.is_active == True
        )
    ).group_by(func.to_char(Transaction.date, 'YYYY-MM-DD' if group_by == 'day' else 'YYYY-MM')).order_by(
        func.to_char(Transaction.date, 'YYYY-MM-DD' if group_by == 'day' else 'YYYY-MM')
    )

    income_result = await db.execute(income_stmt)
    income_rows = income_result.fetchall()

    # 构建支出趋势查询
    expense_stmt = select(
        func.to_char(Transaction.date, 'YYYY-MM-DD' if group_by == 'day' else 'YYYY-MM').label('date_group'),
        func.sum(Transaction.amount).label('total')
    ).where(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'expense',
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.is_active == True
        )
    ).group_by(func.to_char(Transaction.date, 'YYYY-MM-DD' if group_by == 'day' else 'YYYY-MM')).order_by(
        func.to_char(Transaction.date, 'YYYY-MM-DD' if group_by == 'day' else 'YYYY-MM')
    )

    expense_result = await db.execute(expense_stmt)
    expense_rows = expense_result.fetchall()

    # 将结果转换为字典以便于查找
    income_dict = {str(row.date_group): float(row.total or 0) for row in income_rows}
    expense_dict = {str(row.date_group): float(row.total or 0) for row in expense_rows}

    # 生成时间范围内所有的日期组
    trend_data = []

    # 根据分组类型生成时间序列
    current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    if group_by == 'day':
        end_point = end_date.replace(hour=23, minute=59, second=59)
        while current <= end_point:
            date_key = current.strftime('%Y-%m-%d')
            income_val = income_dict.get(date_key, 0)
            expense_val = expense_dict.get(date_key, 0)

            trend_data.append({
                "date": date_key,
                "income": income_val,
                "expense": expense_val,
                "net": income_val - expense_val
            })
            current += timedelta(days=1)
    else:  # 按月分组
        from datetime import date
        import calendar

        start_year, start_month = current.year, current.month
        end_year, end_month = end_date.year, end_date.month

        while (current.year < end_year) or (current.year == end_year and current.month <= end_month):
            date_key = current.strftime('%Y-%m')
            income_val = income_dict.get(date_key, 0)
            expense_val = expense_dict.get(date_key, 0)

            trend_data.append({
                "date": date_key,
                "income": income_val,
                "expense": expense_val,
                "net": income_val - expense_val
            })

            # 移动到下个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

    return {
        "trend_data": trend_data,
        "group_by": group_by,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }


@router.get("/monthly-report")
async def get_monthly_report(
    db: AsyncSession = Depends(get_db),
    year: int = Query(..., description="Year for the report"),
    month: int = Query(..., description="Month for the report"),
    user_id: int = Query(..., description="User ID")
):
    """月度报表汇总"""
    # 计算指定月份的第一天和最后一天
    from datetime import date
    import calendar

    # 获取当月第一天和最后一天
    start_date = datetime(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime(year, month, last_day, 23, 59, 59)

    # 获取月度摘要
    summary = await get_summary(db, start_date, end_date, user_id)

    # 获取分类分析
    category_analysis = await get_category_analysis(db, start_date, end_date, user_id, "expense")

    # 获取预算执行情况
    budgets = await crud.budget.get_monthly_budgets(db, user_id, year, month)

    budget_performance = []
    for budget in budgets:
        updated_budget = await crud.budget.update_budget_spent_amount(db, budget.id)
        budget_performance.append({
            "id": updated_budget.id,
            "name": updated_budget.name,
            "category_name": updated_budget.category.name if updated_budget.category else "Unknown",
            "budget_amount": float(updated_budget.amount),
            "spent_amount": float(updated_budget.spent_amount),
            "percentage_used": updated_budget.spent_percentage,
            "is_over_spent": updated_budget.is_over_spent
        })

    return {
        "summary": summary,
        "category_analysis": category_analysis,
        "budget_performance": budget_performance,
        "report_period": {
            "year": year,
            "month": month
        }
    }


@router.get("/budget-performance")
async def get_detailed_budget_performance(
    db: AsyncSession = Depends(get_db),
    start_date: datetime = Query(..., description="Start date for the analysis"),
    end_date: datetime = Query(..., description="End date for the analysis"),
    user_id: int = Query(..., description="User ID")
):
    """预算执行情况详细分析"""
    # 获取该时间段内所有预算
    stmt = select(Budget).where(
        and_(
            Budget.user_id == user_id,
            Budget.period_start <= end_date,
            Budget.period_end >= start_date,
            Budget.is_active == True
        )
    )

    budgets_result = await db.execute(stmt)
    budgets = budgets_result.scalars().all()

    budget_details = []
    for budget in budgets:
        # 更新预算的花费金额
        updated_budget = await crud.budget.update_budget_spent_amount(db, budget.id)

        budget_details.append({
            "id": updated_budget.id,
            "name": updated_budget.name,
            "category_name": updated_budget.category.name if updated_budget.category else "Unknown",
            "budget_amount": float(updated_budget.amount),
            "spent_amount": float(updated_budget.spent_amount),
            "percentage_used": updated_budget.spent_percentage,
            "is_over_spent": updated_budget.is_over_spent,
            "period_start": updated_budget.period_start,
            "period_end": updated_budget.period_end
        })

    return {
        "budgets": budget_details,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }