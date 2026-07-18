from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import enum
from backend.database import Base


class PropertyType(str, enum.Enum):
    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    OTHER = "other"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    city = Column(String, index=True)
    state = Column(String, index=True)
    zip_code = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geometry("POINT", srid=4326), index=True)

    selling_price = Column(Float)
    property_taxes = Column(Float, nullable=True)
    listing_url = Column(String)

    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Float, nullable=True)
    square_feet = Column(Integer, nullable=True)
    property_type = Column(Enum(PropertyType), default=PropertyType.SINGLE_FAMILY)

    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    area = relationship("Area", back_populates="properties")
    analysis = relationship("InvestmentAnalysis", back_populates="property")
    rental_comparables = relationship("RentalComparable", back_populates="property")
