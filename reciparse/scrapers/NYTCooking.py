import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class NYTCookingScraper(BaseScraper):
    """Scraper for NYT Cooking (cooking.nytimes.com)."""

    _DOMAIN = "cooking.nytimes.com"

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == "cooking.nytimes.com"

    def scrape(self, url: str) -> RecipeData:
        response = self._session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_time(soup, "prep"),
            cook_time=self._parse_time(soup, "cook"),
            servings=self._parse_servings(soup),
            url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_=re.compile(r"recipe-title|pantry--title"))
        if tag:
            return tag.get_text(strip=True)
        og = soup.find("meta", property="og:title")
        return og["content"].strip() if og else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_=re.compile(r"recipe-topnote-metadata|recipe-introduction"))
        if tag:
            return tag.get_text(" ", strip=True)
        meta = soup.find("meta", attrs={"name": "description"})
        return meta["content"].strip() if meta else ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", class_=re.compile(r"ingredient"))
        return [li.get_text(" ", strip=True) for li in items if li.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", class_=re.compile(r"preparation-step"))
        return [li.get_text(" ", strip=True) for li in items if li.get_text(strip=True)]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        """kind is 'prep' or 'cook'."""
        label_re = re.compile(kind, re.IGNORECASE)
        for dt in soup.find_all("dt"):
            if label_re.search(dt.get_text()):
                dd = dt.find_next_sibling("dd")
                if dd:
                    return dd.get_text(strip=True)
        return ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find("span", class_=re.compile(r"yield|servings"))
        return tag.get_text(strip=True) if tag else ""
