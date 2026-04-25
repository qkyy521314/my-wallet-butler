from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models.account import Account
from .schemas.account import AccountCreate, AccountUpdate


class CRUDAccount:
    async def get(self, db: AsyncSession, id: int) -> Optional[Account]:
        result = await db.execute(select(Account).where(Account.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Account]:
        result = await db.execute(select(Account).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: AccountCreate) -> Account:
        db_obj = Account(
            name=obj_in.name,
            account_type=obj_in.account_type,
            balance=obj_in.balance,
            currency=obj_in.currency,
            description=obj_in.description,
            is_active=obj_in.is_active,
            user_id=obj_in.user_id,  # This might need adjustment depending on auth implementation
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: Account, obj_in: Union[AccountUpdate, Dict[str, Any]]
    ) -> Account:
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

    async def remove(self, db: AsyncSession, id: int) -> Account:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


account = CRUDAccount()