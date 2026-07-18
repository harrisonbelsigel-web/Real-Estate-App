from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.app.models.property import PropertyType


class PropertyBase(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str
    latitude: float
    longitude: float
    selling_price: float
    listing_url: str
    property_taxes: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    property_type: PropertyType = PropertyType.SINGLE_FAMILY
    area_id: Optional[int] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    selling_price: Optional[float] = None
    listing_url: Optional[str] = None
    property_taxes: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    property_type: Optional[PropertyType] = None
    area_id: Optional[int] = None


class PropertyResponse(PropertyBase):
    id: int
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True
