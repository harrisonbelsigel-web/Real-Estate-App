from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum
from backend.database import Base


class ScrapingStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapingLog(Base):
    __tablename__ = "scraping_logs"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, nullable=True)
    area_name = Column(String)

    status = Column(Enum(ScrapingStatus), default=ScrapingStatus.PENDING)
    properties_found = Column(Integer, default=0)
    properties_analyzed = Column(Integer, default=0)

    error_message = Column(String, nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
