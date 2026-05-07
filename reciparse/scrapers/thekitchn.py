from __future__ import annotations

import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class TheKitchnScraper(BaseScraper):
    """Scraper for thekitchn.com recipes."""

    _DOMAIN = "thekitchn.com"

    @classmethod
    def supports(cls, url: str) -> bool:
        return cls._DOMAIN in url

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
            url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find("h1", class_=re.compile(r"Recipe__title|Heading"))
        if tag:
            return tag.get_text(strip=True)
        tag = soup.find("h1")
        return tag.get_text(strip=True) if tag else None

    def _parse_description(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find("div", class_=re.compile(r"Recipe__description|recipe-summary"))
        if tag:
            return tag.get_text(strip=True)
        meta = soup.find("meta", attrs={"name": "description"})
        return meta["content"] if meta and meta.get("content") else None

    def _parse_ingredients(self, soup: BeautifulSoup) -> List[str]:
        container = soup.find("ul", class_=re.compile(r"Recipe__ingredients|ingredient"))
        if container:
            return [
                li.get_text(strip=True)
                for li in container.find_all("li")
                if li.get_text(strip=True)
            ]
        return []

    def _parse_instructions(self, soup: BeautifulSoup) -> List[str]:
        container = soup.find("ol", class_=re.compile(r"Recipe__instructions|instruction|step"))
        if container:
            return [
                li.get_text(strip=True)
                for li in container.find_all("li")
                if li.get_text(strip=True)
            ]
        return []

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> Optional[str]:
        tag = soup.find(attrs={"data-recipe-time-type": re.compile(kind, re.I)})
        if tag:
            return tag.get_text(strip=True)
        label = soup.find(string=re.compile(kind, re.I))
        if label and label.parent:
            sibling = label.parent.find_next_sibling()
            return sibling.get_text(strip=True) if sibling else None
        return None

    def _parse_servings(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find(attrs={"data-recipe-servings": True})
        if tag:
            return tag["data-recipe-servings"]
        label = soup.find(string=re.compile(r"serves|servings", re.I))
        if label and label.parent:
            sibling = label.parent.find_next_sibling()
            return sibling.get_text(strip=True) if sibling else None
        return None
