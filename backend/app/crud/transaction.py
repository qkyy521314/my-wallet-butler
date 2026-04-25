from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models.transaction import Transaction
from .schemas.transaction import TransactionCreate, TransactionUpdate


class CRUDTransaction:
    async def get(self, db: AsyncSession, id: int) -> Optional[Transaction]:
        result = await db.execute(select(Transaction).where(Transaction.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        result = await db.execute(select(Transaction).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: TransactionCreate) -> Transaction:
        db_obj = Transaction(
            amount=obj_in.amount,
            description=obj_in.description,
            transaction_type=obj_in.transaction_type,
            category_id=obj_in.category_id,
            account_id=obj_in.account_id,
            from_account_id=obj_in.from_account_id,
            to_account_id=obj_in.to_account_id,
            date=obj_in.date,
            is_active=obj_in.is_active,
            user_id=obj_in.user_id,  # This might need adjustment depending on auth implementation
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: Transaction, obj_in: Union[TransactionUpdate, Dict[str, Any]]
    ) -> Transaction:
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

    async def remove(self, db: AsyncSession, id: int) -> Transaction:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


transaction = CRUDTransaction()