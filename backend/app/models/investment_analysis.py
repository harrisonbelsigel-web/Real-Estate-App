from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class InvestmentAnalysis(Base):
    __tablename__ = "investment_analysis"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)

    rental_estimate = Column(Float, nullable=True)
    annual_rental_income = Column(Float, nullable=True)
    calculated_cap_rate = Column(Float, nullable=True)

    cap_rate_vs_median = Column(Float, nullable=True)

    insurance_estimate = Column(Float, nullable=True)
    property_tax_annual = Column(Float, nullable=True)

    meets_minimum_threshold = Column(Boolean, default=False)
    meets_area_threshold = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    property = relationship("Property", back_populates="analysis")
    area = relationship("Area", back_populates="analysis")
