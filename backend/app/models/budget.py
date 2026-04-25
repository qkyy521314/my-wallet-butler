from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    spent_amount = Column(Numeric(10, 2), default=0.00)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_over_spent = Column(Boolean, default=False)  # 是否超支
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category")

    def __repr__(self):
        return f"<Budget(id={self.id}, name='{self.name}', amount={self.amount})>"

    @property
    def spent_percentage(self):
        """计算预算执行百分比"""
        if self.amount == 0:
            return 0
        return round((self.spent_amount / self.amount) * 100, 2)

    @property
    def is_exceeded(self):
        """判断是否超支"""
        return self.spent_amount > self.amount