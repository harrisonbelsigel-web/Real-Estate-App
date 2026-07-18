from math import radians, sin, cos, asin, sqrt
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.app.models import Property, RentalComparable, PropertyType


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in miles."""
    if None in (lat1, lon1, lat2, lon2):
        return float("inf")
    r = 3958.7613  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


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
        Find rental comparables for a target property using Haversine distance.
        Auto-expands search radius (3mi -> 5mi -> 10mi) if fewer than MIN_COMPS
        size-matched rentals are found.
        Returns (comparables, search_radius_used).
        """
        # Pull all candidate rentals for the city/state once, then filter by
        # computed distance in Python (works on SQLite or Postgres alike).
        candidates = db.query(Property).filter(
            and_(
                Property.property_type == PropertyType.MULTI_FAMILY,
                Property.city == city,
                Property.state == state,
            )
        ).all()

        # Precompute distance for each size-matched candidate.
        matched = []
        for rental in candidates:
            if rental.id == target_property.id:
                continue
            if not RentalComparableAnalyzer.matches_size_criteria(rental, target_property):
                continue
            distance = haversine_miles(
                target_property.latitude, target_property.longitude,
                rental.latitude, rental.longitude,
            )
            matched.append((distance, rental))

        matched.sort(key=lambda pair: pair[0])

        for radius_miles in [
            RentalComparableAnalyzer.INITIAL_RADIUS_MILES,
            RentalComparableAnalyzer.EXPAND_RADIUS_MILES,
            RentalComparableAnalyzer.MAX_RADIUS_MILES
        ]:
            within = [(d, r) for d, r in matched if d <= radius_miles]

            if len(within) >= RentalComparableAnalyzer.MIN_COMPS:
                comparable_objs = []
                for distance, rental in within[:RentalComparableAnalyzer.TARGET_COMPS]:
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
