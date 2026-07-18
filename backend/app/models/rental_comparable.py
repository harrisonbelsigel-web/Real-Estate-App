from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class RentalComparable(Base):
    __tablename__ = "rental_comparables"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)

    comparable_address = Column(String)
    comparable_latitude = Column(Float)
    comparable_longitude = Column(Float)
    distance_miles = Column(Float)

    monthly_rent = Column(Float)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    property = relationship("Property", back_populates="rental_comparables")
