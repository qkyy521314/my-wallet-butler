from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # e.g., cash, bank, credit_card, etc.
    balance = Column(Numeric(10, 2), default=0.00)
    currency = Column(String(3), default='CNY')
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="accounts")

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', balance={self.balance})>"


# 在 User 模型中添加反向关系
if not hasattr(User, 'accounts'):
    User.accounts = relationship("Account", back_populates="user", lazy="select")