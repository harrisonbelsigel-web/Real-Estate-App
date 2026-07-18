import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from backend.app.models import Property, InvestmentAnalysis, Area

logger = logging.getLogger(__name__)


class PropertyTaxEstimator:
    STATE_TAX_RATES = {
        "AL": 0.0041, "AK": 0.0084, "AZ": 0.0062, "AR": 0.0062, "CA": 0.0076,
        "CO": 0.0051, "CT": 0.0222, "DE": 0.0057, "FL": 0.0083, "GA": 0.0092,
        "HI": 0.0028, "ID": 0.0084, "IL": 0.0085, "IN": 0.0085, "IA": 0.0157,
        "KS": 0.0137, "KY": 0.0085, "LA": 0.0055, "ME": 0.0132, "MD": 0.0109,
        "MA": 0.0120, "MI": 0.0148, "MN": 0.0113, "MS": 0.0079, "MO": 0.0097,
        "MT": 0.0084, "NE": 0.0173, "NV": 0.0060, "NH": 0.0220, "NJ": 0.0180,
        "NM": 0.0080, "NY": 0.0180, "NC": 0.0084, "ND": 0.0098, "OH": 0.0142,
        "OK": 0.0090, "OR": 0.0097, "PA": 0.0158, "RI": 0.0123, "SC": 0.0075,
        "SD": 0.0131, "TN": 0.0071, "TX": 0.0180, "UT": 0.0060, "VT": 0.0190,
        "VA": 0.0083, "WA": 0.0094, "WV": 0.0058, "WI": 0.0187, "WY": 0.0061,
    }

    @staticmethod
    def estimate_annual_property_tax(purchase_price: float, state: str) -> float:
        rate = PropertyTaxEstimator.STATE_TAX_RATES.get(state, 0.012)
        return purchase_price * rate

    @staticmethod
    def estimate_monthly_property_tax(purchase_price: float, state: str) -> float:
        annual = PropertyTaxEstimator.estimate_annual_property_tax(purchase_price, state)
        return annual / 12


class InsuranceEstimator:
    BASE_ANNUAL_RATE = 0.005
    PROPERTY_TYPE_MULTIPLIERS = {
        "single_family": 1.0,
        "multi_family": 1.3,
        "condo": 0.8,
        "townhouse": 0.9,
        "other": 1.0,
    }

    @staticmethod
    def estimate_annual_insurance(purchase_price: float, property_type: str) -> float:
        multiplier = InsuranceEstimator.PROPERTY_TYPE_MULTIPLIERS.get(property_type, 1.0)
        return purchase_price * InsuranceEstimator.BASE_ANNUAL_RATE * multiplier

    @staticmethod
    def estimate_monthly_insurance(purchase_price: float, property_type: str) -> float:
        annual = InsuranceEstimator.estimate_annual_insurance(purchase_price, property_type)
        return annual / 12


class PropertyFilter:
    @staticmethod
    def filter_properties(
        db: Session,
        area_id: Optional[int] = None,
        min_cap_rate: Optional[float] = 6.0,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        meets_area_threshold: bool = False,
        sort_by: str = "cap_rate",
        order: str = "desc",
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Property], int]:
        """
        Advanced property filtering with multiple criteria.
        Returns (properties, total_count)
        """
        query = db.query(Property).join(InvestmentAnalysis)

        if area_id:
            query = query.filter(Property.area_id == area_id)

        if min_cap_rate:
            query = query.filter(InvestmentAnalysis.calculated_cap_rate >= min_cap_rate)

        if max_price:
            query = query.filter(Property.selling_price <= max_price)

        if min_price:
            query = query.filter(Property.selling_price >= min_price)

        if bedrooms:
            query = query.filter(Property.bedrooms == bedrooms)

        if meets_area_threshold:
            query = query.filter(InvestmentAnalysis.meets_area_threshold == True)

        total_count = query.count()

        if sort_by == "cap_rate":
            if order == "desc":
                query = query.order_by(desc(InvestmentAnalysis.calculated_cap_rate))
            else:
                query = query.order_by(InvestmentAnalysis.calculated_cap_rate)
        elif sort_by == "price":
            if order == "desc":
                query = query.order_by(desc(Property.selling_price))
            else:
                query = query.order_by(Property.selling_price)
        elif sort_by == "rent":
            if order == "desc":
                query = query.order_by(desc(InvestmentAnalysis.rental_estimate))
            else:
                query = query.order_by(InvestmentAnalysis.rental_estimate)

        return query.offset(skip).limit(limit).all(), total_count

    @staticmethod
    def get_area_summary(db: Session, area_id: int) -> dict:
        """Get summary statistics for an area."""
        analyses = db.query(InvestmentAnalysis).filter(
            InvestmentAnalysis.area_id == area_id
        ).all()

        if not analyses:
            return {
                "total_properties": 0,
                "median_cap_rate": None,
                "median_price": None,
                "median_rent": None,
                "average_cap_rate": None,
            }

        cap_rates = sorted([a.calculated_cap_rate for a in analyses if a.calculated_cap_rate])
        prices = sorted([db.query(Property).filter(Property.id == a.property_id).first().selling_price for a in analyses])
        rents = sorted([a.rental_estimate for a in analyses if a.rental_estimate])

        return {
            "total_properties": len(analyses),
            "median_cap_rate": cap_rates[len(cap_rates) // 2] if cap_rates else None,
            "median_price": prices[len(prices) // 2] if prices else None,
            "median_rent": rents[len(rents) // 2] if rents else None,
            "average_cap_rate": sum(cap_rates) / len(cap_rates) if cap_rates else None,
        }
