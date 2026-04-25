from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AccountBase(BaseModel):
    name: str
    account_type: str
    balance: Optional[Decimal] = 0.00
    currency: Optional[str] = "CNY"
    description: Optional[str] = None
    is_active: Optional[bool] = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None
    balance: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AccountInDBBase(AccountBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Account(AccountInDBBase):
    pass


class AccountInDB(AccountInDBBase):
    pass