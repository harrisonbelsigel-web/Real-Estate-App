from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.app.models import Area
from backend.app.schemas import AreaCreate, AreaUpdate, AreaResponse
from backend.app.services.scraper import PropertyScraper
from backend.app.services.scheduler import sync_area_schedules

router = APIRouter(prefix="/api/areas", tags=["areas"])


@router.get("", response_model=List[AreaResponse])
async def list_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Area).offset(skip).limit(limit).all()


@router.get("/{area_id}", response_model=AreaResponse)
async def get_area(area_id: int, db: Session = Depends(get_db)):
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area


@router.post("", response_model=AreaResponse)
async def create_area(area: AreaCreate, db: Session = Depends(get_db)):
    db_area = Area(
        name=area.name,
        city=area.city,
        state=area.state,
        center_latitude=area.center_latitude,
        center_longitude=area.center_longitude,
        radius_miles=area.radius_miles,
        scrape_frequency=area.scrape_frequency,
    )
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    sync_area_schedules()
    return db_area


@router.put("/{area_id}", response_model=AreaResponse)
async def update_area(area_id: int, area: AreaUpdate, db: Session = Depends(get_db)):
    db_area = db.query(Area).filter(Area.id == area_id).first()
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")

    for field, value in area.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_area, field, value)

    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    sync_area_schedules()
    return db_area


@router.delete("/{area_id}")
async def delete_area(area_id: int, db: Session = Depends(get_db)):
    db_area = db.query(Area).filter(Area.id == area_id).first()
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")

    db.delete(db_area)
    db.commit()
    sync_area_schedules()
    return {"detail": "Area deleted"}
