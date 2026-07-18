from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.app.models import Property, InvestmentAnalysis, RentalComparable, Area
from backend.app.schemas.property_detail import PropertyDetailResponse, PropertyListItemResponse, AreaSummaryResponse
from backend.app.services.property_analyzer import PropertyFilter

router = APIRouter(prefix="/api/properties", tags=["properties"])


@router.get("", response_model=dict)
async def list_properties(
    area_id: Optional[int] = Query(None),
    min_cap_rate: Optional[float] = Query(6.0),
    max_price: Optional[float] = Query(None),
    min_price: Optional[float] = Query(None),
    bedrooms: Optional[int] = Query(None),
    meets_area_threshold: bool = Query(False),
    sort_by: str = Query("cap_rate", regex="^(cap_rate|price|rent)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    List properties with advanced filtering and sorting.

    Query Parameters:
    - area_id: Filter by area
    - min_cap_rate: Minimum cap rate (default 6%)
    - max_price: Maximum selling price
    - min_price: Minimum selling price
    - bedrooms: Filter by number of bedrooms
    - meets_area_threshold: Only show properties above area median cap rate
    - sort_by: Sort by cap_rate, price, or rent
    - order: asc or desc
    - skip: Pagination offset
    - limit: Results per page (max 500)
    """
    properties, total_count = PropertyFilter.filter_properties(
        db,
        area_id=area_id,
        min_cap_rate=min_cap_rate,
        max_price=max_price,
        min_price=min_price,
        bedrooms=bedrooms,
        meets_area_threshold=meets_area_threshold,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )

    items = []
    for prop in properties:
        analysis = db.query(InvestmentAnalysis).filter(
            InvestmentAnalysis.property_id == prop.id
        ).first()

        item = {
            "id": prop.id,
            "address": prop.address,
            "city": prop.city,
            "state": prop.state,
            "selling_price": prop.selling_price,
            "bedrooms": prop.bedrooms,
            "bathrooms": prop.bathrooms,
            "calculated_cap_rate": analysis.calculated_cap_rate if analysis else None,
            "rental_estimate": analysis.rental_estimate if analysis else None,
            "meets_minimum_threshold": analysis.meets_minimum_threshold if analysis else False,
            "meets_area_threshold": analysis.meets_area_threshold if analysis else False,
        }
        items.append(item)

    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "items": items,
    }


@router.get("/{property_id}", response_model=dict)
async def get_property_details(property_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific property."""
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    analysis = db.query(InvestmentAnalysis).filter(
        InvestmentAnalysis.property_id == property_id
    ).first()

    rental_comps = db.query(RentalComparable).filter(
        RentalComparable.property_id == property_id
    ).all()

    return {
        "id": prop.id,
        "address": prop.address,
        "city": prop.city,
        "state": prop.state,
        "zip_code": prop.zip_code,
        "latitude": prop.latitude,
        "longitude": prop.longitude,
        "selling_price": prop.selling_price,
        "property_taxes": prop.property_taxes,
        "bedrooms": prop.bedrooms,
        "bathrooms": prop.bathrooms,
        "square_feet": prop.square_feet,
        "property_type": prop.property_type,
        "listing_url": prop.listing_url,
        "created_at": prop.created_at,
        "last_updated": prop.last_updated,
        "analysis": {
            "id": analysis.id,
            "calculated_cap_rate": analysis.calculated_cap_rate,
            "rental_estimate": analysis.rental_estimate,
            "annual_rental_income": analysis.annual_rental_income,
            "cap_rate_vs_median": analysis.cap_rate_vs_median,
            "insurance_estimate": analysis.insurance_estimate,
            "property_tax_annual": analysis.property_tax_annual,
            "meets_minimum_threshold": analysis.meets_minimum_threshold,
            "meets_area_threshold": analysis.meets_area_threshold,
        } if analysis else None,
        "rental_comparables": [
            {
                "id": comp.id,
                "comparable_address": comp.comparable_address,
                "comparable_latitude": comp.comparable_latitude,
                "comparable_longitude": comp.comparable_longitude,
                "distance_miles": comp.distance_miles,
                "monthly_rent": comp.monthly_rent,
                "bedrooms": comp.bedrooms,
                "bathrooms": comp.bathrooms,
            }
            for comp in rental_comps
        ],
    }


@router.get("/area/{area_id}/summary", response_model=dict)
async def get_area_summary(area_id: int, db: Session = Depends(get_db)):
    """Get investment summary statistics for an area."""
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    summary = PropertyFilter.get_area_summary(db, area_id)

    return {
        "area_id": area_id,
        "area_name": area.name,
        "total_properties": summary["total_properties"],
        "median_cap_rate": summary["median_cap_rate"],
        "median_price": summary["median_price"],
        "median_rent": summary["median_rent"],
        "average_cap_rate": summary["average_cap_rate"],
    }
