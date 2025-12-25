from sqlalchemy import Column, String, Date, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class UCReport(Base, TimestampMixin):
    """Universal Credit monthly assessment period report snapshot."""
    __tablename__ = "uc_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Assessment period
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False)
    
    # Reported figures (cash basis)
    total_income = Column(Numeric(10, 2), nullable=False)
    total_expenses = Column(Numeric(10, 2), nullable=False)
    net_profit = Column(Numeric(10, 2), nullable=False)
    
    # Metadata
    reported_at = Column(Date, nullable=True)  # When user marked as reported to UC
    notes = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="uc_reports")
