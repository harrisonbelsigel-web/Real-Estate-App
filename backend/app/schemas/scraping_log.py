from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.app.models.scraping_log import ScrapingStatus


class ScrapingLogResponse(BaseModel):
    id: int
    area_id: Optional[int] = None
    area_name: str
    status: ScrapingStatus
    properties_found: int
    properties_analyzed: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
