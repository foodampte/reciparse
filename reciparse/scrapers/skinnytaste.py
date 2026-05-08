import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class SkinnyTasteScraper(BaseScraper):
    """Scraper for skinnytaste.com recipes."""

    _DOMAIN = "skinnytaste.com"

    @classmethod
    def supports(cls, url: str) -> bool:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == cls._DOMAIN

    def scrape(self, url: str) -> RecipeData:
        response = requests.get(url, timeout=10, headers={"User-Agent": "reciparse/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_prep_time(soup),
            cook_time=self._parse_cook_time(soup),
            servings=self._parse_servings(soup),
            source_url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h2", class_=re.compile(r"wprm-recipe-name"))
        if tag:
            return tag.get_text(strip=True)
        tag = soup.find("h1", class_=re.compile(r"entry-title"))
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_=re.compile(r"wprm-recipe-summary"))
        return tag.get_text(" ", strip=True) if tag else ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", class_=re.compile(r"wprm-recipe-ingredient"))
        return [li.get_text(" ", strip=True) for li in items]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("div", class_=re.compile(r"wprm-recipe-instruction-text"))
        return [div.get_text(" ", strip=True) for div in items]

    def _parse_prep_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find("span", class_=re.compile(r"wprm-recipe-prep_time-container"))
        return tag.get_text(strip=True) if tag else ""

    def _parse_cook_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find("span", class_=re.compile(r"wprm-recipe-cook_time-container"))
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find("span", class_=re.compile(r"wprm-recipe-servings-container"))
        return tag.get_text(strip=True) if tag else ""
