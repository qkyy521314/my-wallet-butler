from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from ..models.account import Account
from ..schemas.account import AccountCreate, AccountUpdate


class CRUDAccount:
    async def get(self, db: AsyncSession, id: int, user_id: int = None) -> Optional[Account]:
        stmt = select(Account).where(Account.id == id)
        if user_id:
            stmt = stmt.where(Account.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, user_id: int = None,
        account_type: str = None, is_active: bool = None
    ) -> tuple[List[Account], int]:
        stmt = select(Account)

        # 添加用户过滤条件
        if user_id:
            stmt = stmt.where(Account.user_id == user_id)

        # 添加账户类型筛选
        if account_type:
            stmt = stmt.where(Account.account_type == account_type)

        # 添加激活状态筛选
        if is_active is not None:
            stmt = stmt.where(Account.is_active == is_active)

        # 计算总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        # 查询结果
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        accounts = result.scalars().all()

        return accounts, total

    async def create(self, db: AsyncSession, obj_in: AccountCreate, user_id: int) -> Account:
        db_obj = Account(
            name=obj_in.name,
            account_type=obj_in.account_type,
            balance=obj_in.balance or 0.00,
            currency=obj_in.currency,
            description=obj_in.description,
            is_active=obj_in.is_active,
            user_id=user_id,
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

    async def remove(self, db: AsyncSession, id: int, user_id: int = None) -> Account:
        stmt = select(Account).where(Account.id == id)
        if user_id:
            stmt = stmt.where(Account.user_id == user_id)
        result = await db.execute(stmt)
        obj = result.scalars().first()

        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def update_balance(self, db: AsyncSession, account_id: int, amount: float) -> Account:
        """更新账户余额"""
        stmt = select(Account).where(Account.id == account_id)
        result = await db.execute(stmt)
        account = result.scalars().first()

        if account:
            # 更新余额
            account.balance = float(account.balance) + amount
            db.add(account)
            await db.commit()
            await db.refresh(account)
        return account


account = CRUDAccount()