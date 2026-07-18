from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RentalComparableBase(BaseModel):
    property_id: Optional[int] = None
    comparable_address: str
    comparable_latitude: float
    comparable_longitude: float
    distance_miles: float
    monthly_rent: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None


class RentalComparableResponse(RentalComparableBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
