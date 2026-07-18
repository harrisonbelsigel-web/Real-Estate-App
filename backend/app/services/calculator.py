from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models import Property, RentalComparable, InvestmentAnalysis, Area


class CapRateCalculator:
    MIN_CAP_RATE = 6.0

    @staticmethod
    def calculate_rental_estimate(rental_comps: List[RentalComparable]) -> Optional[float]:
        if not rental_comps:
            return None

        total_rent = sum(comp.monthly_rent for comp in rental_comps)
        return total_rent / len(rental_comps)

    @staticmethod
    def calculate_cap_rate(annual_rental_income: float, purchase_price: float) -> Optional[float]:
        if purchase_price <= 0:
            return None
        return (annual_rental_income / purchase_price) * 100

    @staticmethod
    def calculate_property_tax_estimate(purchase_price: float, state: str) -> float:
        state_tax_rates = {
            "NY": 0.018,
            "MA": 0.012,
            "OH": 0.014,
            "TN": 0.007,
            "OK": 0.009,
            "TX": 0.018,
            "CT": 0.022,
        }
        rate = state_tax_rates.get(state, 0.012)
        return purchase_price * rate

    @staticmethod
    def calculate_insurance_estimate(purchase_price: float, property_type: str) -> float:
        annual_insurance_rate = 0.005
        return purchase_price * annual_insurance_rate

    @staticmethod
    def analyze_property(
        db: Session,
        property_obj: Property,
        rental_comps: List[RentalComparable],
        area: Optional[Area] = None
    ) -> Optional[InvestmentAnalysis]:
        rental_estimate = CapRateCalculator.calculate_rental_estimate(rental_comps)

        if rental_estimate is None:
            return None

        annual_rental_income = rental_estimate * 12
        cap_rate = CapRateCalculator.calculate_cap_rate(annual_rental_income, property_obj.selling_price)

        if cap_rate is None or cap_rate < CapRateCalculator.MIN_CAP_RATE:
            return None

        property_tax = CapRateCalculator.calculate_property_tax_estimate(
            property_obj.selling_price,
            property_obj.state
        )
        insurance = CapRateCalculator.calculate_insurance_estimate(
            property_obj.selling_price,
            property_obj.property_type
        )

        cap_rate_vs_median = None
        meets_area_threshold = False

        if area and area.median_cap_rate:
            cap_rate_vs_median = cap_rate - area.median_cap_rate
            meets_area_threshold = cap_rate >= area.median_cap_rate

        analysis = InvestmentAnalysis(
            property_id=property_obj.id,
            area_id=area.id if area else None,
            rental_estimate=rental_estimate,
            annual_rental_income=annual_rental_income,
            calculated_cap_rate=cap_rate,
            cap_rate_vs_median=cap_rate_vs_median,
            insurance_estimate=insurance,
            property_tax_annual=property_tax,
            meets_minimum_threshold=cap_rate >= CapRateCalculator.MIN_CAP_RATE,
            meets_area_threshold=meets_area_threshold
        )

        return analysis
