from sqlalchemy import Column, String, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class Income(Base, TimestampMixin):
    """Cash-received income transaction."""
    __tablename__ = "incomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction details
    date_received = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=False)
    
    # Tax calculation metadata
    tax_year = Column(String(7), nullable=False, index=True)  # e.g., "2024-25"
    tax_ruleset_version = Column(String, nullable=False)  # Tracks which ruleset was used
    
    # Relationships
    user = relationship("User", back_populates="incomes")
