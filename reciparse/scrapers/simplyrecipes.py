import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class SimplyRecipesScraper(BaseScraper):
    """Scraper for simplyrecipes.com."""

    _DOMAIN = "simplyrecipes.com"

    def __init__(self):
        super().__init__()

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == "simplyrecipes.com"

    def scrape(self, url: str) -> RecipeData:
        response = requests.get(url, timeout=10, headers={"User-Agent": "reciparse/1.0"})
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
            source_url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_=re.compile(r"heading", re.I))
        if tag is None:
            tag = soup.find("h1")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_=re.compile(r"article-subheading|recipe-intro", re.I))
        if tag is None:
            tag = soup.find("meta", attrs={"name": "description"})
            return tag["content"].strip() if tag else ""
        return tag.get_text(strip=True)

    def _parse_ingredients(self, soup: BeautifulSoup) -> list:
        container = soup.find("ul", class_=re.compile(r"structured-ingredients", re.I))
        if container is None:
            container = soup.find("ul", class_=re.compile(r"ingredient", re.I))
        if container is None:
            return []
        return [
            li.get_text(" ", strip=True)
            for li in container.find_all("li")
            if li.get_text(strip=True)
        ]

    def _parse_instructions(self, soup: BeautifulSoup) -> list:
        container = soup.find("ol", class_=re.compile(r"instruction|direction|step", re.I))
        if container is None:
            return []
        return [
            li.get_text(" ", strip=True)
            for li in container.find_all("li")
            if li.get_text(strip=True)
        ]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        label_re = re.compile(kind, re.I)
        tag = soup.find(attrs={"data-testid": label_re})
        if tag is None:
            tag = soup.find(class_=re.compile(rf"{kind}[_-]?time", re.I))
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find(attrs={"data-testid": re.compile(r"serving", re.I)})
        if tag is None:
            tag = soup.find(class_=re.compile(r"serving", re.I))
        return tag.get_text(strip=True) if tag else ""
