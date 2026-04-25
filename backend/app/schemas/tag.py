from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TagBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#000000"  # Hex color code
    is_active: Optional[bool] = True


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class TagInDBBase(TagBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Tag(TagInDBBase):
    pass


class TagInDB(TagInDBBase):
    pass