from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import engine, get_db, Base
from backend.app.models import Property, Area, RentalComparable, InvestmentAnalysis, ScrapingLog
import os

app = FastAPI(title="Real Estate Investment App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Real Estate Investment App API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/properties")
async def get_properties(
    skip: int = 0,
    limit: int = 100,
    area_id: int = None,
    min_cap_rate: float = None,
    db: Session = Depends(get_db)
):
    query = db.query(Property)

    if area_id:
        query = query.filter(Property.area_id == area_id)

    if min_cap_rate:
        query = query.join(InvestmentAnalysis).filter(
            InvestmentAnalysis.calculated_cap_rate >= min_cap_rate
        )

    return query.offset(skip).limit(limit).all()

@app.get("/api/properties/{property_id}")
async def get_property(property_id: int, db: Session = Depends(get_db)):
    return db.query(Property).filter(Property.id == property_id).first()

@app.get("/api/areas")
async def get_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Area).offset(skip).limit(limit).all()

@app.get("/api/areas/{area_id}")
async def get_area(area_id: int, db: Session = Depends(get_db)):
    return db.query(Area).filter(Area.id == area_id).first()

@app.get("/api/analysis/{property_id}")
async def get_property_analysis(property_id: int, db: Session = Depends(get_db)):
    return db.query(InvestmentAnalysis).filter(
        InvestmentAnalysis.property_id == property_id
    ).first()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
