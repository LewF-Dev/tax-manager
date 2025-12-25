from sqlalchemy import Column, String, Date, Numeric, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class TaxSnapshot(Base, TimestampMixin):
    """Annual tax year summary snapshot for audit trail."""
    __tablename__ = "tax_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tax year
    tax_year = Column(String(7), nullable=False, index=True)  # e.g., "2024-25"
    tax_year_start = Column(Date, nullable=False)
    tax_year_end = Column(Date, nullable=False)
    
    # Summary figures
    total_income = Column(Numeric(10, 2), nullable=False)
    total_expenses = Column(Numeric(10, 2), nullable=False)
    net_profit = Column(Numeric(10, 2), nullable=False)
    
    # Tax calculations
    income_tax = Column(Numeric(10, 2), nullable=False)
    ni_class2 = Column(Numeric(10, 2), nullable=False)
    ni_class4 = Column(Numeric(10, 2), nullable=False)
    total_tax = Column(Numeric(10, 2), nullable=False)
    
    # Ruleset used
    tax_ruleset_version = Column(String, nullable=False)
    ruleset_data = Column(JSON, nullable=False)  # Store actual ruleset for historical accuracy
    
    # Relationships
    user = relationship("User", back_populates="tax_snapshots")
