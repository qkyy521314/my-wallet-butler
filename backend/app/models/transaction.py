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
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    from_account_id = Column(Integer, ForeignKey("accounts.id"))  # For transfers
    to_account_id = Column(Integer, ForeignKey("accounts.id"))    # For transfers
    date = Column(DateTime(timezone=True), nullable=False)
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

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, type='{self.transaction_type}')>"


# 在 User 模型中添加反向关系
if not hasattr(User, 'transactions'):
    User.transactions = relationship("Transaction", back_populates="user", lazy="select")