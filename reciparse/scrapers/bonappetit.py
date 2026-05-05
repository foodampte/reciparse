import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from reciparse.scrapers.base import BaseScraper, RecipeData


class BonAppetitScraper(BaseScraper):
    """Scraper for bonappetit.com recipes."""

    DOMAIN = "bonappetit.com"

    @classmethod
    def supports(cls, url: str) -> bool:
        return "bonappetit.com" in url

    def scrape(self, url: str) -> RecipeData:
        response = requests.get(url, timeout=10, headers={"User-Agent": "reciparse/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_time(soup, "prepTime"),
            cook_time=self._parse_time(soup, "cookTime"),
            servings=self._parse_servings(soup),
            source_url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find("h1", {"data-testid": "ContentHeaderHed"})
        if tag:
            return tag.get_text(strip=True)
        og = soup.find("meta", {"property": "og:title"})
        return og["content"] if og else None

    def _parse_description(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find("div", {"class": re.compile(r"dek|description", re.I)})
        if tag:
            return tag.get_text(strip=True)
        meta = soup.find("meta", {"name": "description"})
        return meta["content"] if meta else None

    def _parse_ingredients(self, soup: BeautifulSoup) -> list:
        items = soup.find_all("div", {"data-testid": "IngredientList"})
        if not items:
            items = soup.find_all("li", {"class": re.compile(r"ingredient", re.I)})
        return [i.get_text(strip=True) for i in items if i.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup) -> list:
        steps = soup.find_all("p", {"class": re.compile(r"step|instruction", re.I)})
        return [s.get_text(strip=True) for s in steps if s.get_text(strip=True)]

    def _parse_time(self, soup: BeautifulSoup, time_type: str) -> Optional[str]:
        tag = soup.find(attrs={"itemprop": time_type})
        return tag.get_text(strip=True) if tag else None

    def _parse_servings(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find(attrs={"itemprop": "recipeYield"})
        return tag.get_text(strip=True) if tag else None
