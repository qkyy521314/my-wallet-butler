from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# 创建异步引擎
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 创建基础模型
Base = declarative_base()


# 获取数据库会话的依赖函数
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session