from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class TransactionTag(Base):
    __tablename__ = "transaction_tags"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="tags")
    tag = relationship("Tag", back_populates="transactions")

    def __repr__(self):
        return f"<TransactionTag(transaction_id={self.transaction_id}, tag_id={self.tag_id})>"