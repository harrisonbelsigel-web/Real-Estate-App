# Real Estate Investment App

A full-stack application that helps identify high-cap-rate real estate investment opportunities across the country.

## Features

- Scrape property listings from Zillow, Redfin, and other platforms
- Calculate cap rates based on local rental market data
- Filter properties with cap rates >= 6% and above local median
- Display comprehensive investment metrics
- Admin panel for managing tracked cities/areas
- Interactive map and property filtering

## Tech Stack

**Backend:** Python, FastAPI, PostgreSQL, PostGIS
**Frontend:** React, TypeScript, React Map GL
**Scraping:** Playwright, BeautifulSoup

## Setup

### Prerequisites

- Python 3.10+
- Node.js 16+
- PostgreSQL 13+ (with PostGIS extension)

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/harrisonbelsigel-web/Real-Estate-App.git
cd Real-Estate-App
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database connection details
```

5. Initialize the database:
```bash
# Create PostGIS extension (first time only)
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Run migrations (when available)
alembic upgrade head
```

6. Run the backend:
```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## API Endpoints

### Properties
- `GET /api/properties` - List properties
- `GET /api/properties/{id}` - Get property details
- `GET /api/analysis/{property_id}` - Get investment analysis

### Areas
- `GET /api/areas` - List tracked areas
- `GET /api/areas/{id}` - Get area details
- `POST /admin/areas` - Create new area (admin)
- `PUT /admin/areas/{id}` - Update area (admin)
- `DELETE /admin/areas/{id}` - Delete area (admin)

### Scraping
- `POST /admin/scrape` - Trigger scraping for an area
- `GET /admin/scraping-jobs` - View scraping status

## Project Structure

```
Real-Estate-App/
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── api/          # API routes
│   │   │   ├── areas.py       # Area CRUD endpoints
│   │   │   └── scraping.py    # Scraping job endpoints
│   │   ├── services/     # Business logic
│   │   │   ├── scraper.py           # Main scraping orchestration
│   │   │   ├── zillow_scraper.py    # Zillow listings scraper
│   │   │   ├── redfin_scraper.py    # Redfin listings scraper
│   │   │   ├── rental_analyzer.py   # Find rental comparables
│   │   │   └── calculator.py        # Cap rate calculations
│   │   └── main.py       # FastAPI app
│   ├── scripts/
│   │   └── init_areas.py # Initialize database with default areas
│   ├── database.py       # Database configuration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## How It Works

## API Endpoints Reference

### Properties
- `GET /api/properties` - List properties with advanced filtering
  - Query params: `area_id`, `min_cap_rate` (default 6%), `max_price`, `min_price`, `bedrooms`, `meets_area_threshold`, `sort_by` (cap_rate|price|rent), `order` (asc|desc), `skip`, `limit`
  - Returns: Paginated list with cap rate and rental data
- `GET /api/properties/{id}` - Get full property details including analysis and rental comps
- `GET /api/properties/area/{area_id}/summary` - Get area statistics (median cap rate, price, rent)

### Areas
- `GET /api/areas` - List all tracked areas
- `GET /api/areas/{id}` - Get area details
- `POST /api/areas` - Create new area
- `PUT /api/areas/{id}` - Update area
- `DELETE /api/areas/{id}` - Delete area

### Admin/Scraping
- `POST /admin/scrape/{area_id}` - Trigger scraping job (async background task)
- `GET /admin/scraping-jobs` - View scraping history and status
- `GET /admin/scraping-jobs/{id}` - Get specific scraping job details

## Scraping Process

1. **Trigger Scrape**: Call `POST /admin/scrape/{area_id}` to start scraping
2. **Property Collection**: Scrapes Zillow & Redfin for for-sale listings in the area
3. **Find Comparables**: For each property, finds rental listings with similar specs (±1 bed, ±1 bath, ±20% sqft)
4. **Auto-Expand**: If fewer than 5 rentals found, automatically expands search radius (3mi → 5mi → 10mi)
5. **Cap Rate Calculation**: 
   - Average monthly rent from comparable properties
   - Annual income = avg rent × 12
   - Cap rate = Annual income / Purchase price
6. **Filter & Store**: Only saves properties with cap rate ≥ 6%
7. **Calculate Medians**: Updates area's median cap rate for threshold comparison

### Rental Comparable Matching

Properties must match within:
- **Bedrooms**: ±1
- **Bathrooms**: ±1  
- **Square Footage**: ±20%
- **Distance**: 3-10 miles (auto-expands if needed)

## Development Roadmap

### Phase 1: ✅ Core Backend & Data Model
- ✅ FastAPI setup
- ✅ PostgreSQL + PostGIS
- ✅ Data models
- ✅ Basic CRUD endpoints

### Phase 2: ✅ Scraping Infrastructure
- Build Zillow scraper
- Build rental property scraper
- Implement geographic search
- Cap rate calculation

### Phase 3: ✅ Analysis & Filtering
- Property tax lookup
- Insurance estimation
- Advanced filtering

### Phase 4: Frontend
- React app setup
- Map visualization
- Property listings
- Admin panel

### Phase 5: Polish & Optimization
- Caching
- Background jobs
- Performance tuning

## Contributing

1. Create a feature branch
2. Make your changes
3. Push and create a pull request

## License

MIT
