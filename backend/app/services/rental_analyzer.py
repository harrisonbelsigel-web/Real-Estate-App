from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from geoalchemy2.functions import ST_DWithin, ST_Distance
from backend.app.models import Property, RentalComparable, PropertyType


class RentalComparableAnalyzer:
    INITIAL_RADIUS_MILES = 3.0
    EXPAND_RADIUS_MILES = 5.0
    MAX_RADIUS_MILES = 10.0
    MIN_COMPS = 5
    TARGET_COMPS = 10

    SIZE_TOLERANCE = {
        "bedrooms_delta": 1,
        "bathrooms_delta": 1,
        "sqft_percent": 0.20
    }

    @staticmethod
    def miles_to_meters(miles: float) -> float:
        return miles * 1609.34

    @staticmethod
    def matches_size_criteria(
        rental_property: Property,
        target_property: Property
    ) -> bool:
        if not rental_property.bedrooms or not target_property.bedrooms:
            return True

        bed_diff = abs(rental_property.bedrooms - target_property.bedrooms)
        if bed_diff > RentalComparableAnalyzer.SIZE_TOLERANCE["bedrooms_delta"]:
            return False

        if not rental_property.bathrooms or not target_property.bathrooms:
            return True

        bath_diff = abs(rental_property.bathrooms - target_property.bathrooms)
        if bath_diff > RentalComparableAnalyzer.SIZE_TOLERANCE["bathrooms_delta"]:
            return False

        if not rental_property.square_feet or not target_property.square_feet:
            return True

        sqft_ratio = rental_property.square_feet / target_property.square_feet
        if sqft_ratio < (1 - RentalComparableAnalyzer.SIZE_TOLERANCE["sqft_percent"]) or \
           sqft_ratio > (1 + RentalComparableAnalyzer.SIZE_TOLERANCE["sqft_percent"]):
            return False

        return True

    @staticmethod
    def find_comparable_rentals(
        db: Session,
        target_property: Property,
        city: str,
        state: str
    ) -> Tuple[List[RentalComparable], float]:
        """
        Find rental comparables for a target property.
        Auto-expands search radius if fewer than MIN_COMPS found.
        Returns (comparables, search_radius_used)
        """
        for radius_miles in [
            RentalComparableAnalyzer.INITIAL_RADIUS_MILES,
            RentalComparableAnalyzer.EXPAND_RADIUS_MILES,
            RentalComparableAnalyzer.MAX_RADIUS_MILES
        ]:
            radius_meters = RentalComparableAnalyzer.miles_to_meters(radius_miles)

            rentals = db.query(Property).filter(
                and_(
                    Property.property_type == PropertyType.MULTI_FAMILY,
                    Property.city == city,
                    Property.state == state,
                    ST_DWithin(
                        Property.geom,
                        target_property.geom,
                        radius_meters
                    )
                )
            ).all()

            matching_rentals = [
                rental for rental in rentals
                if RentalComparableAnalyzer.matches_size_criteria(rental, target_property)
            ]

            if len(matching_rentals) >= RentalComparableAnalyzer.MIN_COMPS:
                comparable_objs = []
                for rental in matching_rentals[:RentalComparableAnalyzer.TARGET_COMPS]:
                    distance = db.query(
                        func.ST_Distance(
                            target_property.geom,
                            rental.geom
                        ) / 1609.34
                    ).scalar()

                    comp = RentalComparable(
                        comparable_address=rental.address,
                        comparable_latitude=rental.latitude,
                        comparable_longitude=rental.longitude,
                        distance_miles=distance,
                        monthly_rent=rental.selling_price / 12 if rental.selling_price else 0
                    )
                    comparable_objs.append(comp)

                return comparable_objs, radius_miles

        return [], RentalComparableAnalyzer.MAX_RADIUS_MILES
