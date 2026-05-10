from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    amount: Decimal
    description: Optional[str] = None
    transaction_type: str  # income, expense, transfer
    category_id: Optional[int] = None
    account_id: int
    from_account_id: Optional[int] = None  # For transfers
    to_account_id: Optional[int] = None    # For transfers
    date: Optional[datetime] = None
    is_active: Optional[bool] = True


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_type: Optional[str] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    from_account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    date: Optional[datetime] = None
    is_active: Optional[bool] = None


class TransactionInDBBase(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Transaction(TransactionInDBBase):
    pass


class TransactionInDB(TransactionInDBBase):
    pass