from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from ..models.transaction_tag import TransactionTag
from ..models.tag import Tag


class CRUDTransactionTag:
    async def create(self, db: AsyncSession, transaction_id: int, tag_id: int) -> TransactionTag:
        db_obj = TransactionTag(
            transaction_id=transaction_id,
            tag_id=tag_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove_by_transaction_and_tag(self, db: AsyncSession, transaction_id: int, tag_id: int) -> bool:
        result = await db.execute(
            select(TransactionTag).where(
                and_(TransactionTag.transaction_id == transaction_id, TransactionTag.tag_id == tag_id)
            )
        )
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False

    async def get_by_transaction(self, db: AsyncSession, transaction_id: int) -> List[Tag]:
        from ..models.transaction import Transaction
        result = await db.execute(
            select(Tag)
            .join(TransactionTag)
            .where(TransactionTag.transaction_id == transaction_id)
        )
        return result.scalars().all()

    async def get_by_tag(self, db: AsyncSession, tag_id: int) -> List[Tag]:
        from ..models.transaction import Transaction
        result = await db.execute(
            select(Transaction)
            .join(TransactionTag)
            .where(TransactionTag.tag_id == tag_id)
        )
        return result.scalars().all()

    async def bulk_create_for_transaction(self, db: AsyncSession, transaction_id: int, tag_ids: List[int]) -> List[TransactionTag]:
        """为交易批量创建标签关系"""
        objects = []
        for tag_id in tag_ids:
            db_obj = TransactionTag(
                transaction_id=transaction_id,
                tag_id=tag_id
            )
            objects.append(db_obj)

        db.add_all(objects)
        await db.commit()

        # 刷新所有对象
        for obj in objects:
            await db.refresh(obj)

        return objects


transaction_tag = CRUDTransactionTag()