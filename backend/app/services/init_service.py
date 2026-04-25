import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.category import Category
from ..database import Base
from ..config import settings


# 预设分类数据
PRESET_CATEGORIES = [
    # 预设收入分类
    {"name": "工资", "category_type": "income", "description": "薪资收入"},
    {"name": "奖金", "category_type": "income", "description": "奖金收入"},
    {"name": "投资收益", "category_type": "income", "description": "股票、基金等投资收益"},
    {"name": "兼职", "category_type": "income", "description": "兼职工作收入"},
    {"name": "其他", "category_type": "income", "description": "其他收入类型"},

    # 预设支出分类
    {"name": "餐饮", "category_type": "expense", "description": "食物、饮料消费"},
    {"name": "交通", "category_type": "expense", "description": "交通费用"},
    {"name": "购物", "category_type": "expense", "description": "日常购物消费"},
    {"name": "娱乐", "category_type": "expense", "description": "娱乐活动支出"},
    {"name": "住房", "category_type": "expense", "description": "房租、房贷、水电费等"},
    {"name": "医疗", "category_type": "expense", "description": "医疗健康支出"},
    {"name": "教育", "category_type": "expense", "description": "教育学习支出"},
    {"name": "其他", "category_type": "expense", "description": "其他支出类型"},
]


async def init_preset_categories(db: AsyncSession, user_id: int):
    """初始化预设分类"""
    for cat_data in PRESET_CATEGORIES:
        # 检查分类是否已存在
        existing_cat = await db.execute(
            select(Category).where(
                Category.name == cat_data["name"],
                Category.user_id == user_id,
                Category.category_type == cat_data["category_type"]
            )
        )
        if not existing_cat.scalars().first():
            category = Category(
                name=cat_data["name"],
                category_type=cat_data["category_type"],
                description=cat_data["description"],
                user_id=user_id,
                is_active=True
            )
            db.add(category)

    await db.commit()


if __name__ == "__main__":
    # 示例用法
    async def main():
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as db:
            # 这里需要传入特定用户的ID来初始化分类
            await init_preset_categories(db, user_id=1)

    asyncio.run(main())