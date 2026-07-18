import asyncio
import re
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright, Page
import logging

logger = logging.getLogger(__name__)


class ZillowScraper:
    BASE_URL = "https://www.zillow.com"
    TIMEOUT = 30000

    @staticmethod
    async def search_properties(
        city: str,
        state: str,
        property_type: str = "for_sale"
    ) -> List[Dict[str, Any]]:
        """
        Scrape properties from Zillow for a given city/state.
        Returns list of property data dictionaries.
        """
        properties = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            try:
                search_url = ZillowScraper._build_search_url(city, state, property_type)
                await page.goto(search_url, wait_until="networkidle", timeout=ZillowScraper.TIMEOUT)

                await page.wait_for_selector("[data-testid='property-card']", timeout=10000)

                property_elements = await page.query_selector_all("[data-testid='property-card']")
                logger.info(f"Found {len(property_elements)} properties on Zillow for {city}, {state}")

                for element in property_elements:
                    try:
                        prop_data = await ZillowScraper._extract_property_data(element, page)
                        if prop_data:
                            properties.append(prop_data)
                    except Exception as e:
                        logger.warning(f"Error extracting property: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error scraping Zillow: {e}")
            finally:
                await browser.close()

        return properties

    @staticmethod
    def _build_search_url(city: str, state: str, property_type: str) -> str:
        search_term = f"{city}, {state}"
        base = f"{ZillowScraper.BASE_URL}/homes/for_sale"
        return f"{base}/?searchQueryState={{'pagination':{{}}, 'usersSearchTerm':'{search_term}'}}"

    @staticmethod
    async def _extract_property_data(element, page: Page) -> Optional[Dict[str, Any]]:
        try:
            address = await element.query_selector("[data-testid='property-address']")
            address_text = await address.inner_text() if address else None

            price = await element.query_selector("span[data-testid='property-price']")
            price_text = await price.inner_text() if price else None

            link = await element.query_selector("a[data-testid='property-card-link']")
            url = await link.get_attribute("href") if link else None

            price_value = ZillowScraper._parse_price(price_text)

            if not address_text or not price_value:
                return None

            city_state = await ZillowScraper._extract_location(element)

            return {
                "address": address_text.strip(),
                "city": city_state.get("city", ""),
                "state": city_state.get("state", ""),
                "zip_code": city_state.get("zip", ""),
                "selling_price": price_value,
                "listing_url": url,
                "latitude": None,
                "longitude": None,
                "bedrooms": None,
                "bathrooms": None,
                "square_feet": None,
            }
        except Exception as e:
            logger.warning(f"Error extracting property data: {e}")
            return None

    @staticmethod
    def _parse_price(price_text: Optional[str]) -> Optional[float]:
        if not price_text:
            return None

        price_match = re.search(r"\$?([\d,]+)", price_text)
        if price_match:
            try:
                return float(price_match.group(1).replace(",", ""))
            except ValueError:
                return None

        return None

    @staticmethod
    async def _extract_location(element) -> Dict[str, str]:
        try:
            location_elem = await element.query_selector("[data-testid='property-location']")
            if location_elem:
                location_text = await location_elem.inner_text()
                parts = location_text.split(",")
                if len(parts) >= 2:
                    return {
                        "city": parts[0].strip(),
                        "state": parts[1].strip()[:2].upper(),
                        "zip": ""
                    }
        except Exception as e:
            logger.warning(f"Error extracting location: {e}")

        return {"city": "", "state": "", "zip": ""}
