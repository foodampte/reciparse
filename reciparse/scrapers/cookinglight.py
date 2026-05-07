"""Scraper for cookinglight.com recipes."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class CookingLightScraper(BaseScraper):
    """Scraper for CookingLight.com."""

    _DOMAIN = "cookinglight.com"

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == "cookinglight.com"

    def scrape(self, url: str) -> RecipeData:
        response = requests.get(url, timeout=10)
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
        tag = soup.find("h1", class_=re.compile(r"recipe-title|headline"))
        if tag:
            return tag.get_text(strip=True)
        og = soup.find("meta", property="og:title")
        return og["content"].strip() if og else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_=re.compile(r"recipe-summary|description"))
        if tag:
            return tag.get_text(" ", strip=True)
        meta = soup.find("meta", attrs={"name": "description"})
        return meta["content"].strip() if meta else ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ul", class_=re.compile(r"ingredient"))
        if not container:
            return []
        return [
            li.get_text(" ", strip=True)
            for li in container.find_all("li")
            if li.get_text(strip=True)
        ]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ol", class_=re.compile(r"instruction|direction|step"))
        if not container:
            return []
        return [
            li.get_text(" ", strip=True)
            for li in container.find_all("li")
            if li.get_text(strip=True)
        ]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        label_re = re.compile(kind, re.IGNORECASE)
        label = soup.find(class_=re.compile(r"recipe-meta-item"))
        if label:
            for item in soup.find_all(class_=re.compile(r"recipe-meta-item")):
                text = item.get_text(" ", strip=True)
                if label_re.search(text):
                    return text
        return ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        for item in soup.find_all(class_=re.compile(r"recipe-meta-item")):
            text = item.get_text(" ", strip=True)
            if re.search(r"serving", text, re.IGNORECASE):
                return text
        return ""
