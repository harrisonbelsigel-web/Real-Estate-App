from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import engine, get_db, Base
from backend.app.models import Property, Area, RentalComparable, InvestmentAnalysis, ScrapingLog
from backend.app.api.areas import router as areas_router
from backend.app.api.scraping import router as scraping_router
from backend.app.api.properties import router as properties_router
from backend.app.services.scheduler import start_scheduler, shutdown_scheduler
import logging
import os

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(title="Real Estate Investment App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(areas_router)
app.include_router(scraping_router)
app.include_router(properties_router)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()

@app.on_event("shutdown")
async def shutdown():
    shutdown_scheduler()

@app.get("/")
async def root():
    return {"message": "Real Estate Investment App API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
