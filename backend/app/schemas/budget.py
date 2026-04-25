from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class BudgetBase(BaseModel):
    name: str
    category_id: int
    amount: Decimal
    period_start: datetime
    period_end: datetime
    description: Optional[str] = None
    is_active: Optional[bool] = True


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    amount: Optional[Decimal] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class BudgetInDBBase(BudgetBase):
    id: int
    user_id: int
    spent_amount: Optional[Decimal] = 0.00
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Budget(BudgetInDBBase):
    pass


class BudgetInDB(BudgetInDBBase):
    pass