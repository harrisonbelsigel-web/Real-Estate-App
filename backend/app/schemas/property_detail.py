from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RentalComparableDetail(BaseModel):
    id: int
    comparable_address: str
    comparable_latitude: float
    comparable_longitude: float
    distance_miles: float
    monthly_rent: float
    bedrooms: Optional[int]
    bathrooms: Optional[float]

    class Config:
        from_attributes = True


class PropertyDetailResponse(BaseModel):
    id: int
    address: str
    city: str
    state: str
    zip_code: str
    latitude: float
    longitude: float

    selling_price: float
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    square_feet: Optional[int]
    property_type: str

    listing_url: str
    created_at: datetime
    last_updated: datetime

    analysis: Optional[dict] = None
    rental_comparables: List[RentalComparableDetail] = []

    class Config:
        from_attributes = True


class PropertyListItemResponse(BaseModel):
    id: int
    address: str
    city: str
    state: str
    selling_price: float
    bedrooms: Optional[int]
    bathrooms: Optional[float]

    calculated_cap_rate: Optional[float] = None
    rental_estimate: Optional[float] = None
    meets_minimum_threshold: bool = False
    meets_area_threshold: bool = False

    class Config:
        from_attributes = True


class AreaSummaryResponse(BaseModel):
    area_id: int
    area_name: str
    total_properties: int
    median_cap_rate: Optional[float]
    median_price: Optional[float]
    median_rent: Optional[float]
    average_cap_rate: Optional[float]
