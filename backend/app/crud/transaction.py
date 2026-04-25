from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from ..models.transaction import Transaction
from ..schemas.transaction import TransactionCreate, TransactionUpdate


class CRUDTransaction:
    async def get(self, db: AsyncSession, id: int, user_id: int = None) -> Optional[Transaction]:
        stmt = select(Transaction).where(Transaction.id == id)
        if user_id:
            stmt = stmt.where(Transaction.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, user_id: int = None,
        transaction_type: str = None, is_active: bool = None, account_id: int = None,
        category_id: int = None, start_date: str = None, end_date: str = None
    ) -> tuple[List[Transaction], int]:
        stmt = select(Transaction)

        # 添加用户过滤条件
        if user_id:
            stmt = stmt.where(Transaction.user_id == user_id)

        # 添加交易类型筛选
        if transaction_type:
            stmt = stmt.where(Transaction.transaction_type == transaction_type)

        # 添加激活状态筛选
        if is_active is not None:
            stmt = stmt.where(Transaction.is_active == is_active)

        # 添加账户筛选
        if account_id:
            stmt = stmt.where(
                (Transaction.account_id == account_id) |
                (Transaction.from_account_id == account_id) |
                (Transaction.to_account_id == account_id)
            )

        # 添加分类筛选
        if category_id:
            stmt = stmt.where(Transaction.category_id == category_id)

        # 添加日期范围筛选
        if start_date:
            stmt = stmt.where(Transaction.date >= start_date)
        if end_date:
            stmt = stmt.where(Transaction.date <= end_date)

        # 按日期降序排列
        stmt = stmt.order_by(Transaction.date.desc())

        # 计算总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        # 查询结果
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        transactions = result.scalars().all()

        return transactions, total

    async def create(self, db: AsyncSession, obj_in: TransactionCreate, user_id: int) -> Transaction:
        db_obj = Transaction(
            amount=obj_in.amount,
            description=obj_in.description,
            transaction_type=obj_in.transaction_type,
            category_id=obj_in.category_id,
            account_id=obj_in.account_id,
            from_account_id=getattr(obj_in, 'from_account_id', None),
            to_account_id=getattr(obj_in, 'to_account_id', None),
            date=getattr(obj_in, 'date', func.now()),
            is_active=obj_in.is_active,
            user_id=user_id,
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

    async def remove(self, db: AsyncSession, id: int, user_id: int = None) -> Transaction:
        stmt = select(Transaction).where(Transaction.id == id)
        if user_id:
            stmt = stmt.where(Transaction.user_id == user_id)
        result = await db.execute(stmt)
        obj = result.scalars().first()

        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def create_transfer(self, db: AsyncSession, transfer_data: dict, user_id: int) -> Transaction:
        """创建转账交易，同时更新相关账户余额"""
        from ..crud.account import account as account_crud

        # 获取转出和转入账户
        from_account = await account_crud.get(db, transfer_data['from_account_id'], user_id)
        to_account = await account_crud.get(db, transfer_data['to_account_id'], user_id)

        if not from_account or not to_account:
            raise ValueError("Invalid from_account_id or to_account_id")

        if float(from_account.balance) < float(transfer_data['amount']):
            raise ValueError("Insufficient balance in source account")

        # 创建转账交易记录
        transfer = Transaction(
            amount=transfer_data['amount'],
            description=transfer_data.get('description', ''),
            transaction_type='transfer',
            category_id=transfer_data.get('category_id'),  # 转账可选择性地指定分类
            from_account_id=transfer_data['from_account_id'],
            to_account_id=transfer_data['to_account_id'],
            date=transfer_data.get('date', func.now()),
            is_active=transfer_data.get('is_active', True),
            user_id=user_id
        )

        db.add(transfer)
        await db.flush()  # 获取ID但不提交事务，确保后续操作在同一事务中

        # 更新账户余额
        # 转出账户减少余额
        from_account.balance = float(from_account.balance) - float(transfer_data['amount'])
        db.add(from_account)

        # 转入账户增加余额
        to_account.balance = float(to_account.balance) + float(transfer_data['amount'])
        db.add(to_account)

        await db.commit()
        await db.refresh(transfer)

        return transfer


transaction = CRUDTransaction()