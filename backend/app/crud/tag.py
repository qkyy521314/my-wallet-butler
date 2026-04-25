from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.tag import Tag
from ..schemas.tag import TagCreate, TagUpdate


class CRUDTag:
    async def get(self, db: AsyncSession, id: int) -> Optional[Tag]:
        result = await db.execute(select(Tag).where(Tag.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Tag]:
        result = await db.execute(select(Tag).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: TagCreate) -> Tag:
        db_obj = Tag(
            name=obj_in.name,
            description=obj_in.description,
            color=obj_in.color,
            is_active=obj_in.is_active,
            user_id=obj_in.user_id,  # This might need adjustment depending on auth implementation
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: Tag, obj_in: Union[TagUpdate, Dict[str, Any]]
    ) -> Tag:
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

    async def remove(self, db: AsyncSession, id: int) -> Tag:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


tag = CRUDTag()