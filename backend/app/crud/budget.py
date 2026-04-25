from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models.budget import Budget
from .schemas.budget import BudgetCreate, BudgetUpdate


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


budget = CRUDBudget()