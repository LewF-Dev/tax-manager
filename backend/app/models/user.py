from sqlalchemy import Column, String, Boolean, Date, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User account with trading and UC configuration."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Supabase Auth ID
    supabase_id = Column(String, unique=True, nullable=False, index=True)
    
    # Profile
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    
    # Trading configuration
    trading_start_date = Column(Date, nullable=True)
    
    # UC configuration
    uc_enabled = Column(Boolean, default=False, nullable=False)
    uc_assessment_day = Column(Integer, nullable=True)  # Day of month UC period starts (1-28)
    
    # Tax configuration
    tax_set_aside_percentage = Column(Numeric(5, 2), default=20.00, nullable=False)
    
    # Subscription
    stripe_customer_id = Column(String, unique=True, nullable=True, index=True)
    subscription_status = Column(String, default="inactive", nullable=False)  # active, inactive, past_due, canceled
    subscription_id = Column(String, nullable=True)
    
    # Relationships
    incomes = relationship("Income", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    uc_reports = relationship("UCReport", back_populates="user", cascade="all, delete-orphan")
    tax_snapshots = relationship("TaxSnapshot", back_populates="user", cascade="all, delete-orphan")
