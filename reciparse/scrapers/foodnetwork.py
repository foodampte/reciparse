"""Scraper for FoodNetwork.com recipes."""

from bs4 import BeautifulSoup
import requests

from .base import BaseScraper, RecipeData


class FoodNetworkScraper(BaseScraper):
    """Scraper implementation for FoodNetwork.com."""

    DOMAIN = "foodnetwork.com"

    def supports(self, url: str) -> bool:
        return self.DOMAIN in url

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
        tag = soup.find("span", class_="o-AssetTitle__a-HeadlineText")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_="o-AssetDescription__a-Description")
        return tag.get_text(strip=True) if tag else ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("span", class_="o-Ingredients__a-Ingredient--CheckboxLabel")
        return [item.get_text(strip=True) for item in items if item.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", class_="o-Method__m-Step")
        return [item.get_text(strip=True) for item in items if item.get_text(strip=True)]

    def _parse_prep_time(self, soup: BeautifulSoup) -> str | None:
        return self._parse_time_field(soup, "Prep")

    def _parse_cook_time(self, soup: BeautifulSoup) -> str | None:
        return self._parse_time_field(soup, "Cook")

    def _parse_time_field(self, soup: BeautifulSoup, label: str) -> str | None:
        for block in soup.find_all("li", class_="o-RecipeInfo__Item"):
            span = block.find("span", class_="o-RecipeInfo__a-Headline")
            if span and label.lower() in span.get_text(strip=True).lower():
                value = block.find("span", class_="o-RecipeInfo__a-Description")
                if value:
                    return value.get_text(strip=True)
        return None

    def _parse_servings(self, soup: BeautifulSoup) -> str | None:
        return self._parse_time_field(soup, "Yield")
