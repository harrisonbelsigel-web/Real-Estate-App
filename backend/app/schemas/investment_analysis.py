from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InvestmentAnalysisResponse(BaseModel):
    id: int
    property_id: int
    area_id: Optional[int] = None

    rental_estimate: Optional[float] = None
    annual_rental_income: Optional[float] = None
    calculated_cap_rate: Optional[float] = None
    cap_rate_vs_median: Optional[float] = None

    insurance_estimate: Optional[float] = None
    property_tax_annual: Optional[float] = None

    meets_minimum_threshold: bool = False
    meets_area_threshold: bool = False

    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True
