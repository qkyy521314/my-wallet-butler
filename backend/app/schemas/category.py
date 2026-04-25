from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    category_type: str  # income or expense
    description: Optional[str] = None
    is_active: Optional[bool] = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    category_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryInDBBase(CategoryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Category(CategoryInDBBase):
    pass


class CategoryInDB(CategoryInDBBase):
    pass