from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from backend.database import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    city = Column(String)
    state = Column(String)

    center_latitude = Column(Float)
    center_longitude = Column(Float)
    geom = Column(Geometry("POINT", srid=4326), index=True)

    radius_miles = Column(Float, default=5.0)

    median_cap_rate = Column(Float, nullable=True)
    median_rent = Column(Float, nullable=True)

    # "manual" (default), "daily", "weekly", or "monthly"
    scrape_frequency = Column(String, default="manual")
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    properties = relationship("Property", back_populates="area")
    analysis = relationship("InvestmentAnalysis", back_populates="area")
