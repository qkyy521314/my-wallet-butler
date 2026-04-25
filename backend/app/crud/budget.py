from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from datetime import datetime
from ..models.budget import Budget
from ..models.transaction import Transaction
from ..schemas.budget import BudgetCreate, BudgetUpdate


class CRUDBudget:
    async def get(self, db: AsyncSession, id: int) -> Optional[Budget]:
        result = await db.execute(select(Budget).where(Budget.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Budget]:
        result = await db.execute(select(Budget).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: BudgetCreate) -> Budget:
        db_obj = Budget(
            name=obj_in.name,
            category_id=obj_in.category_id,
            amount=obj_in.amount,
            period_start=obj_in.period_start,
            period_end=obj_in.period_end,
            description=obj_in.description,
            is_active=obj_in.is_active,
            user_id=obj_in.user_id,  # This might need adjustment depending on auth implementation
            spent_amount=0.00,  # 默认支出金额为0
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: Budget, obj_in: Union[BudgetUpdate, Dict[str, Any]]
    ) -> Budget:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, id: int) -> Budget:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def get_monthly_budgets(self, db: AsyncSession, user_id: int, year: int, month: int) -> List[Budget]:
        """获取指定用户和月份的预算"""
        from datetime import datetime
        from sqlalchemy import extract

        result = await db.execute(
            select(Budget).where(
                and_(
                    Budget.user_id == user_id,
                    extract('year', Budget.period_start) == year,
                    extract('month', Budget.period_start) <= month,
                    extract('year', Budget.period_end) == year,
                    extract('month', Budget.period_end) >= month,
                    Budget.is_active == True
                )
            )
        )
        return result.scalars().all()

    async def calculate_category_spending(self, db: AsyncSession, user_id: int, category_id: int, start_date: datetime, end_date: datetime) -> float:
        """计算指定分类在指定时间段内的支出"""
        result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.category_id == category_id,
                    Transaction.transaction_type == 'expense',
                    Transaction.date >= start_date,
                    Transaction.date <= end_date,
                    Transaction.is_active == True
                )
            )
        )
        spending = result.scalar()
        return spending if spending is not None else 0.0

    async def update_budget_spent_amount(self, db: AsyncSession, budget_id: int) -> Budget:
        """更新预算的已花费金额"""
        budget = await self.get(db, budget_id)
        if budget:
            spent = await self.calculate_category_spending(
                db, budget.user_id, budget.category_id, budget.period_start, budget.period_end
            )
            budget.spent_amount = spent
            budget.is_over_spent = spent > budget.amount
            db.add(budget)
            await db.commit()
            await db.refresh(budget)
        return budget


budget = CRUDBudget()