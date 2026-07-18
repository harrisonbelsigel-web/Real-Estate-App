import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models import Property, Area, RentalComparable, InvestmentAnalysis, ScrapingLog, PropertyType
from backend.app.models.scraping_log import ScrapingStatus
from backend.app.services.zillow_scraper import ZillowScraper
from backend.app.services.redfin_scraper import RedfinScraper
from backend.app.services.rental_analyzer import RentalComparableAnalyzer
from backend.app.services.calculator import CapRateCalculator
from backend.app.services.cache import cache

logger = logging.getLogger(__name__)


class PropertyScraper:
    @staticmethod
    async def scrape_area(
        db: Session,
        area: Area,
        scrapers: List[str] = ["zillow", "redfin"]
    ) -> ScrapingLog:
        """
        Scrape properties for an area from multiple sources.
        Calculate cap rates and only store properties with cap rate >= 6%.
        """
        log = ScrapingLog(
            area_id=area.id,
            area_name=area.name,
            status=ScrapingStatus.IN_PROGRESS
        )
        db.add(log)
        db.commit()

        try:
            all_properties = []

            if "zillow" in scrapers:
                zillow_props = await ZillowScraper.search_properties(area.city, area.state)
                all_properties.extend(zillow_props)
                logger.info(f"Zillow found {len(zillow_props)} properties")

            if "redfin" in scrapers:
                redfin_props = await RedfinScraper.search_properties(area.city, area.state)
                all_properties.extend(redfin_props)
                logger.info(f"Redfin found {len(redfin_props)} properties")

            log.properties_found = len(all_properties)

            qualified_properties = []

            for prop_data in all_properties:
                try:
                    property_obj = Property(**prop_data)
                    property_obj.area_id = area.id

                    rental_comps, radius_used = RentalComparableAnalyzer.find_comparable_rentals(
                        db,
                        property_obj,
                        area.city,
                        area.state
                    )

                    if not rental_comps:
                        logger.warning(f"No rental comps found for {property_obj.address}")
                        continue

                    analysis = CapRateCalculator.analyze_property(
                        db,
                        property_obj,
                        rental_comps,
                        area
                    )

                    if analysis is None or analysis.calculated_cap_rate < CapRateCalculator.MIN_CAP_RATE:
                        logger.debug(f"Property {property_obj.address} cap rate below minimum")
                        continue

                    db.add(property_obj)
                    db.flush()

                    analysis.property_id = property_obj.id
                    db.add(analysis)

                    for comp in rental_comps:
                        comp.property_id = property_obj.id
                        db.add(comp)

                    qualified_properties.append(property_obj)
                    log.properties_analyzed += 1

                except Exception as e:
                    logger.error(f"Error processing property: {e}")
                    continue

            db.commit()

            PropertyScraper._update_area_median(db, area)

            log.status = ScrapingStatus.COMPLETED
            log.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error scraping area {area.name}: {e}")
            log.status = ScrapingStatus.FAILED
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()

        db.add(log)
        db.commit()

        # Invalidate cached listings/summaries now that data changed.
        cache.clear()

        return log

    @staticmethod
    def _update_area_median(db: Session, area: Area) -> None:
        """Calculate and update median cap rate for an area."""
        try:
            analyses = db.query(InvestmentAnalysis).filter(
                InvestmentAnalysis.area_id == area.id
            ).all()

            if analyses:
                cap_rates = sorted([a.calculated_cap_rate for a in analyses if a.calculated_cap_rate])
                if cap_rates:
                    median = cap_rates[len(cap_rates) // 2]
                    area.median_cap_rate = median

                rents = sorted([a.rental_estimate for a in analyses if a.rental_estimate])
                if rents:
                    median_rent = rents[len(rents) // 2]
                    area.median_rent = median_rent

                    for analysis in analyses:
                        analysis.meets_area_threshold = (
                            analysis.calculated_cap_rate >= area.median_cap_rate
                        )

            db.add(area)
            db.commit()
        except Exception as e:
            logger.error(f"Error updating area median: {e}")
