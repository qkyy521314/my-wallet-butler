from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category_type = Column(String(20), nullable=False)  # income, expense
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="categories")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.category_type}')>"


# 在 User 模型中添加反向关系
if not hasattr(User, 'categories'):
    User.categories = relationship("Category", back_populates="user", lazy="select")