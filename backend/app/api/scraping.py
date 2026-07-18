from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.app.models import Area, ScrapingLog
from backend.app.schemas import ScrapingLogResponse
from backend.app.services.scraper import PropertyScraper

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/scrape/{area_id}")
async def trigger_scrape(
    area_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    background_tasks.add_task(PropertyScraper.scrape_area, db, area)

    return {
        "detail": f"Scraping started for {area.name}",
        "area_id": area_id,
        "area_name": area.name
    }


@router.get("/scraping-jobs", response_model=List[ScrapingLogResponse])
async def get_scraping_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ScrapingLog).offset(skip).limit(limit).all()


@router.get("/scraping-jobs/{job_id}", response_model=ScrapingLogResponse)
async def get_scraping_job(job_id: int, db: Session = Depends(get_db)):
    log = db.query(ScrapingLog).filter(ScrapingLog.id == job_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Scraping job not found")
    return log
