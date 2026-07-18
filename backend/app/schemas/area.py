from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AreaBase(BaseModel):
    name: str
    city: str
    state: str
    center_latitude: float
    center_longitude: float
    radius_miles: float = 5.0


class AreaCreate(AreaBase):
    pass


class AreaUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None
    radius_miles: Optional[float] = None


class AreaResponse(AreaBase):
    id: int
    median_cap_rate: Optional[float] = None
    median_rent: Optional[float] = None
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True
