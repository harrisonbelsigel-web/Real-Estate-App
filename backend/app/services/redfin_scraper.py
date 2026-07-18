import asyncio
import re
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright, Page
import logging

logger = logging.getLogger(__name__)


class RedfinScraper:
    BASE_URL = "https://www.redfin.com"
    TIMEOUT = 30000

    @staticmethod
    async def search_properties(
        city: str,
        state: str,
        property_type: str = "for_sale"
    ) -> List[Dict[str, Any]]:
        """
        Scrape properties from Redfin for a given city/state.
        Returns list of property data dictionaries.
        """
        properties = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            try:
                search_url = RedfinScraper._build_search_url(city, state)
                await page.goto(search_url, wait_until="networkidle", timeout=RedfinScraper.TIMEOUT)

                await page.wait_for_selector(".HomeCard", timeout=10000)

                property_elements = await page.query_selector_all(".HomeCard")
                logger.info(f"Found {len(property_elements)} properties on Redfin for {city}, {state}")

                for element in property_elements:
                    try:
                        prop_data = await RedfinScraper._extract_property_data(element, page)
                        if prop_data:
                            properties.append(prop_data)
                    except Exception as e:
                        logger.warning(f"Error extracting property: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error scraping Redfin: {e}")
            finally:
                await browser.close()

        return properties

    @staticmethod
    def _build_search_url(city: str, state: str) -> str:
        city_slug = city.lower().replace(" ", "-")
        state_lower = state.lower()
        return f"{RedfinScraper.BASE_URL}/{state_lower}/{city_slug}/homes-for-sale"

    @staticmethod
    async def _extract_property_data(element, page: Page) -> Optional[Dict[str, Any]]:
        try:
            address_elem = await element.query_selector(".HomeCard--address")
            address_text = await address_elem.inner_text() if address_elem else None

            price_elem = await element.query_selector(".HomeCard--price")
            price_text = await price_elem.inner_text() if price_elem else None

            link_elem = await element.query_selector("a")
            url = await link_elem.get_attribute("href") if link_elem else None

            if url and not url.startswith("http"):
                url = f"{RedfinScraper.BASE_URL}{url}"

            price_value = RedfinScraper._parse_price(price_text)

            if not address_text or not price_value:
                return None

            city_state = await RedfinScraper._extract_location(element)

            beds_baths = await RedfinScraper._extract_beds_baths(element)

            return {
                "address": address_text.strip(),
                "city": city_state.get("city", ""),
                "state": city_state.get("state", ""),
                "zip_code": city_state.get("zip", ""),
                "selling_price": price_value,
                "listing_url": url,
                "latitude": None,
                "longitude": None,
                "bedrooms": beds_baths.get("bedrooms"),
                "bathrooms": beds_baths.get("bathrooms"),
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
            location_elem = await element.query_selector(".HomeCard--location")
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

    @staticmethod
    async def _extract_beds_baths(element) -> Dict[str, Optional[int]]:
        try:
            beds_elem = await element.query_selector(".HomeCard--beds")
            baths_elem = await element.query_selector(".HomeCard--baths")

            bedrooms = None
            bathrooms = None

            if beds_elem:
                beds_text = await beds_elem.inner_text()
                beds_match = re.search(r"(\d+)", beds_text)
                bedrooms = int(beds_match.group(1)) if beds_match else None

            if baths_elem:
                baths_text = await baths_elem.inner_text()
                baths_match = re.search(r"([\d.]+)", baths_text)
                bathrooms = float(baths_match.group(1)) if baths_match else None

            return {"bedrooms": bedrooms, "bathrooms": bathrooms}
        except Exception as e:
            logger.warning(f"Error extracting beds/baths: {e}")
            return {"bedrooms": None, "bathrooms": None}
