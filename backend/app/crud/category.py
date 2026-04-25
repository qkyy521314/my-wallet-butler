from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory:
    async def get(self, db: AsyncSession, id: int, user_id: int = None) -> Optional[Category]:
        stmt = select(Category).where(Category.id == id)
        if user_id:
            stmt = stmt.where(Category.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, user_id: int = None,
        category_type: str = None, is_active: bool = None, parent_id: int = None
    ) -> tuple[List[Category], int]:
        stmt = select(Category)

        # 添加用户过滤条件
        if user_id:
            stmt = stmt.where(Category.user_id == user_id)

        # 添加分类类型筛选
        if category_type:
            stmt = stmt.where(Category.category_type == category_type)

        # 添加激活状态筛选
        if is_active is not None:
            stmt = stmt.where(Category.is_active == is_active)

        # 添加父级分类筛选
        if parent_id is not None:
            stmt = stmt.where(Category.parent_id == parent_id)

        # 计算总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        # 查询结果
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        categories = result.scalars().all()

        return categories, total

    async def create(self, db: AsyncSession, obj_in: CategoryCreate, user_id: int) -> Category:
        db_obj = Category(
            name=obj_in.name,
            category_type=obj_in.category_type,
            description=obj_in.description,
            is_active=obj_in.is_active,
            user_id=user_id,
            parent_id=obj_in.parent_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: Category, obj_in: Union[CategoryUpdate, Dict[str, Any]]
    ) -> Category:
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

    async def remove(self, db: AsyncSession, id: int, user_id: int = None) -> Category:
        stmt = select(Category).where(Category.id == id)
        if user_id:
            stmt = stmt.where(Category.user_id == user_id)
        result = await db.execute(stmt)
        obj = result.scalars().first()

        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def get_children(self, db: AsyncSession, parent_id: int, user_id: int = None) -> List[Category]:
        """获取子分类"""
        stmt = select(Category).where(Category.parent_id == parent_id)
        if user_id:
            stmt = stmt.where(Category.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_tree(self, db: AsyncSession, user_id: int, category_type: str = None) -> List[dict]:
        """获取分类树形结构"""
        stmt = select(Category).where(Category.user_id == user_id)
        if category_type:
            stmt = stmt.where(Category.category_type == category_type)
        stmt = stmt.where(Category.is_active == True)

        result = await db.execute(stmt)
        all_categories = result.scalars().all()

        # 构建分类树
        category_dict = {}
        root_categories = []

        # 将所有分类存入字典
        for cat in all_categories:
            category_dict[cat.id] = {
                'id': cat.id,
                'name': cat.name,
                'category_type': cat.category_type,
                'description': cat.description,
                'is_active': cat.is_active,
                'parent_id': cat.parent_id,
                'children': []
            }

        # 构建父子关系
        for cat in all_categories:
            if cat.parent_id is None:
                root_categories.append(category_dict[cat.id])
            else:
                parent_cat = category_dict.get(cat.parent_id)
                if parent_cat:
                    parent_cat['children'].append(category_dict[cat.id])

        return root_categories


category = CRUDCategory()