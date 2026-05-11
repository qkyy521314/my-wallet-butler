from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class TransactionTag(Base):
    __tablename__ = "transaction_tags"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    transaction = relationship("Transaction")
    tag = relationship("Tag")

    def __repr__(self):
        return f"<TransactionTag(transaction_id={self.transaction_id}, tag_id={self.tag_id})>"