"""
Initialize database with default areas.
Run from backend directory: python -m scripts.init_areas
"""

from backend.database import SessionLocal, engine, Base
from backend.app.models import Area

INITIAL_AREAS = [
    {
        "name": "Ithaca, NY",
        "city": "Ithaca",
        "state": "NY",
        "center_latitude": 42.4534,
        "center_longitude": -76.4735,
        "radius_miles": 5.0
    },
    {
        "name": "Boston, MA",
        "city": "Boston",
        "state": "MA",
        "center_latitude": 42.3601,
        "center_longitude": -71.0589,
        "radius_miles": 5.0
    },
    {
        "name": "Syracuse, NY",
        "city": "Syracuse",
        "state": "NY",
        "center_latitude": 43.0481,
        "center_longitude": -76.1474,
        "radius_miles": 5.0
    },
    {
        "name": "Cleveland, OH",
        "city": "Cleveland",
        "state": "OH",
        "center_latitude": 41.4993,
        "center_longitude": -81.6944,
        "radius_miles": 5.0
    },
    {
        "name": "Nashville, TN",
        "city": "Nashville",
        "state": "TN",
        "center_latitude": 36.1627,
        "center_longitude": -86.7816,
        "radius_miles": 5.0
    },
    {
        "name": "East Nashville, TN",
        "city": "Nashville",
        "state": "TN",
        "center_latitude": 36.1627,
        "center_longitude": -86.6816,
        "radius_miles": 5.0
    },
    {
        "name": "Cincinnati, OH",
        "city": "Cincinnati",
        "state": "OH",
        "center_latitude": 39.1019,
        "center_longitude": -84.5074,
        "radius_miles": 5.0
    },
    {
        "name": "Bricktown, OK",
        "city": "Oklahoma City",
        "state": "OK",
        "center_latitude": 35.4676,
        "center_longitude": -97.5164,
        "radius_miles": 5.0
    },
    {
        "name": "Austin, TX",
        "city": "Austin",
        "state": "TX",
        "center_latitude": 30.2672,
        "center_longitude": -97.7431,
        "radius_miles": 5.0
    },
    {
        "name": "Dallas, TX",
        "city": "Dallas",
        "state": "TX",
        "center_latitude": 32.7767,
        "center_longitude": -96.7970,
        "radius_miles": 5.0
    },
    {
        "name": "Truro, Cape Cod, MA",
        "city": "Truro",
        "state": "MA",
        "center_latitude": 42.0522,
        "center_longitude": -70.0617,
        "radius_miles": 5.0
    },
    {
        "name": "New Haven, CT",
        "city": "New Haven",
        "state": "CT",
        "center_latitude": 41.3083,
        "center_longitude": -72.9279,
        "radius_miles": 5.0
    },
    {
        "name": "Toledo, OH",
        "city": "Toledo",
        "state": "OH",
        "center_latitude": 41.6639,
        "center_longitude": -83.5552,
        "radius_miles": 5.0
    },
]


def init_areas():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        for area_data in INITIAL_AREAS:
            existing = db.query(Area).filter(Area.name == area_data["name"]).first()
            if existing:
                print(f"Area {area_data['name']} already exists")
                continue

            area = Area(
                name=area_data["name"],
                city=area_data["city"],
                state=area_data["state"],
                center_latitude=area_data["center_latitude"],
                center_longitude=area_data["center_longitude"],
                radius_miles=area_data["radius_miles"],
                geom=f"POINT({area_data['center_longitude']} {area_data['center_latitude']})"
            )
            db.add(area)
            print(f"Created area: {area_data['name']}")

        db.commit()
        print("Database initialization complete!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_areas()
