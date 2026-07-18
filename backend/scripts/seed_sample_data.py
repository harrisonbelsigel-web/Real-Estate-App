"""
Seed the database with realistic SAMPLE properties so the UI can be explored
before live scraping is tuned. Data is fictional; listing links point to
example.com placeholders.

Everything flows through the real pipeline: rental comps are matched with
RentalComparableAnalyzer (Haversine + size tolerance), cap rates come from
CapRateCalculator, and the >=6% filter + area medians behave exactly as they
will with scraped data.

Run from the repo root: python -m backend.scripts.seed_sample_data
"""

import random

from backend.database import SessionLocal, engine, Base
from backend.app.models import Property, PropertyType, Area
from backend.app.services.rental_analyzer import RentalComparableAnalyzer
from backend.app.services.calculator import CapRateCalculator
from backend.app.services.scraper import PropertyScraper

random.seed(42)

STREETS = [
    "Maple St", "Oak Ave", "Cedar Rd", "Elm St", "Birch Ln", "Walnut Dr",
    "Chestnut Blvd", "Spruce Ct", "Willow Way", "Hickory Pl", "Sycamore St",
    "Poplar Ave", "Magnolia Dr", "Juniper Rd", "Aspen Ct", "Linden St",
]

# Per-city market assumptions: price range for sale listings and typical rent
# per bedroom. Cheaper Midwest/Upstate markets naturally clear the 6% bar;
# pricier ones mostly won't - which demonstrates the filter.
CITY_MARKETS = {
    "Cleveland":  {"state": "OH", "lat": 41.4993, "lon": -81.6944, "zip": "44113",
                   "price": (95_000, 180_000), "rent_per_bed": 520},
    "Toledo":     {"state": "OH", "lat": 41.6639, "lon": -83.5552, "zip": "43604",
                   "price": (85_000, 160_000), "rent_per_bed": 480},
    "Syracuse":   {"state": "NY", "lat": 43.0481, "lon": -76.1474, "zip": "13202",
                   "price": (110_000, 200_000), "rent_per_bed": 560},
    "Ithaca":     {"state": "NY", "lat": 42.4534, "lon": -76.4735, "zip": "14850",
                   "price": (240_000, 380_000), "rent_per_bed": 900},
    "Cincinnati": {"state": "OH", "lat": 39.1019, "lon": -84.5074, "zip": "45202",
                   "price": (120_000, 230_000), "rent_per_bed": 550},
}

RENTALS_PER_CITY = 12
SALES_PER_CITY = 6


def jitter(center: float, spread_deg: float = 0.025) -> float:
    """Random offset within ~1.7 miles of the center."""
    return center + random.uniform(-spread_deg, spread_deg)


def make_address(n: int) -> str:
    return f"{random.randint(100, 9999)} {random.choice(STREETS)}"


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created, skipped = 0, 0

    try:
        for city, m in CITY_MARKETS.items():
            area = db.query(Area).filter(
                Area.city == city, Area.state == m["state"]
            ).first()

            # --- Rental comps: multi-family rows whose selling_price encodes
            #     ANNUAL rent (analyzer derives monthly_rent = selling_price/12)
            for i in range(RENTALS_PER_CITY):
                beds = random.choice([2, 2, 3, 3, 3, 4])
                monthly_rent = beds * m["rent_per_bed"] + random.randint(-100, 150)
                rental = Property(
                    address=make_address(i),
                    city=city,
                    state=m["state"],
                    zip_code=m["zip"],
                    latitude=jitter(m["lat"]),
                    longitude=jitter(m["lon"]),
                    selling_price=monthly_rent * 12,
                    listing_url=f"https://example.com/sample-rental/{city.lower()}-{i}",
                    bedrooms=beds,
                    bathrooms=random.choice([1.0, 1.5, 2.0]),
                    square_feet=beds * 450 + random.randint(-150, 250),
                    property_type=PropertyType.MULTI_FAMILY,
                    area_id=area.id if area else None,
                )
                db.add(rental)
            db.flush()

            # --- For-sale listings run through the real pipeline
            for i in range(SALES_PER_CITY):
                beds = random.choice([2, 3, 3, 3, 4])
                price = random.randint(*m["price"])
                sale = Property(
                    address=make_address(100 + i),
                    city=city,
                    state=m["state"],
                    zip_code=m["zip"],
                    latitude=jitter(m["lat"]),
                    longitude=jitter(m["lon"]),
                    selling_price=price,
                    # Sample data: no real listing exists, so link to the live
                    # Zillow search for the city instead of a dead placeholder.
                    listing_url=f"https://www.zillow.com/homes/for_sale/{city},-{m['state']}_rb/",
                    bedrooms=beds,
                    bathrooms=random.choice([1.0, 1.5, 2.0, 2.5]),
                    square_feet=beds * 480 + random.randint(-150, 300),
                    property_type=PropertyType.SINGLE_FAMILY,
                    area_id=area.id if area else None,
                )

                comps, radius = RentalComparableAnalyzer.find_comparable_rentals(
                    db, sale, city, m["state"]
                )
                if not comps:
                    skipped += 1
                    print(f"  SKIP (no comps): {sale.address}, {city}")
                    continue

                analysis = CapRateCalculator.analyze_property(db, sale, comps, area)
                if analysis is None:
                    skipped += 1
                    print(f"  SKIP (<6% cap): {sale.address}, {city} @ ${price:,}")
                    continue

                db.add(sale)
                db.flush()
                analysis.property_id = sale.id
                db.add(analysis)
                for comp in comps:
                    comp.property_id = sale.id
                    db.add(comp)
                created += 1
                print(f"  KEEP: {sale.address}, {city} @ ${price:,} -> "
                      f"{analysis.calculated_cap_rate:.2f}% cap ({len(comps)} comps, {radius}mi)")

            db.commit()
            if area:
                PropertyScraper._update_area_median(db, area)

        print(f"\nDone. {created} properties saved (cap rate >= 6%), {skipped} filtered out.")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
