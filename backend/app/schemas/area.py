from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

VALID_FREQUENCIES = {"manual", "daily", "weekly", "monthly"}


class AreaBase(BaseModel):
    name: str
    city: str
    state: str
    center_latitude: float
    center_longitude: float
    radius_miles: float = 5.0
    scrape_frequency: str = "manual"

    @field_validator("scrape_frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        if v not in VALID_FREQUENCIES:
            raise ValueError(f"scrape_frequency must be one of {sorted(VALID_FREQUENCIES)}")
        return v


class AreaCreate(AreaBase):
    pass


class AreaUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None
    radius_miles: Optional[float] = None
    scrape_frequency: Optional[str] = None

    @field_validator("scrape_frequency")
    @classmethod
    def validate_frequency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_FREQUENCIES:
            raise ValueError(f"scrape_frequency must be one of {sorted(VALID_FREQUENCIES)}")
        return v


class AreaResponse(AreaBase):
    id: int
    median_cap_rate: Optional[float] = None
    median_rent: Optional[float] = None
    last_scraped_at: Optional[datetime] = None
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True
