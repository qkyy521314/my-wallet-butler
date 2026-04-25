import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+asyncmy://root:password@localhost/wallet_butler")

    # JWT 配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))  # 7 days (7 * 24 * 60)

    # 应用配置
    APP_NAME: str = os.getenv("APP_NAME", "My Wallet Butler")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Redis 配置（可选）
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)


settings = Settings()