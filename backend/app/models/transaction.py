from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255))
    transaction_type = Column(String(20), nullable=False)  # income, expense, transfer
    category_id = Column(Integer, ForeignKey("categories.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))  # 主账户（对于转账来说是目标账户）
    from_account_id = Column(Integer, ForeignKey("accounts.id"))  # 转出账户（仅用于转账）
    to_account_id = Column(Integer, ForeignKey("accounts.id"))    # 转入账户（仅用于转账）
    date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category")
    account = relationship("Account", foreign_keys=[account_id])
    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])
    tags = relationship("Tag", secondary="transaction_tags", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, type='{self.transaction_type}')>"