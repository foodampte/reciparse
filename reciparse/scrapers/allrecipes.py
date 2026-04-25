"""Scraper for AllRecipes.com."""

import requests
from bs4 import BeautifulSoup

from reciparse.scrapers.base import BaseScraper, RecipeData


class AllRecipesScraper(BaseScraper):
    """Scrapes recipe data from allrecipes.com."""

    SUPPORTED_DOMAINS = ["allrecipes.com"]

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; reciparse/1.0; "
            "+https://github.com/you/reciparse)"
        )
    }

    def scrape(self) -> RecipeData:
        response = requests.get(self.url, headers=self.HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = self._parse_title(soup)
        ingredients = self._parse_ingredients(soup)
        instructions = self._parse_instructions(soup)
        description = self._parse_description(soup)
        times = self._parse_times(soup)
        servings = self._parse_servings(soup)
        image_url = self._parse_image(soup)

        return RecipeData(
            title=title,
            url=self.url,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            source="allrecipes.com",
            image_url=image_url,
            servings=servings,
            **times,
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_="article-heading")
        return self._clean_text(tag.get_text()) if tag else "Unknown"

    def _parse_description(self, soup: BeautifulSoup):
        tag = soup.find("p", class_="article-subheading")
        return self._clean_text(tag.get_text()) if tag else None

    def _parse_ingredients(self, soup: BeautifulSoup):
        items = soup.select("li.mm-recipes-structured-ingredients__list-item")
        return [self._clean_text(i.get_text()) for i in items if i.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup):
        steps = soup.select("li.comp.mntl-sc-block-group--LI")
        return [self._clean_text(s.get_text()) for s in steps if s.get_text(strip=True)]

    def _parse_times(self, soup: BeautifulSoup) -> dict:
        result = {"prep_time": None, "cook_time": None, "total_time": None}
        labels = {"Prep Time:": "prep_time", "Cook Time:": "cook_time", "Total Time:": "total_time"}
        for item in soup.select(".mm-recipes-details__item"):
            label_tag = item.select_one(".mm-recipes-details__label")
            value_tag = item.select_one(".mm-recipes-details__value")
            if label_tag and value_tag:
                label = self._clean_text(label_tag.get_text())
                if label in labels:
                    result[labels[label]] = self._clean_text(value_tag.get_text())
        return result

    def _parse_servings(self, soup: BeautifulSoup):
        for item in soup.select(".mm-recipes-details__item"):
            label_tag = item.select_one(".mm-recipes-details__label")
            if label_tag and "Servings:" in label_tag.get_text():
                value_tag = item.select_one(".mm-recipes-details__value")
                return self._clean_text(value_tag.get_text()) if value_tag else None
        return None

    def _parse_image(self, soup: BeautifulSoup):
        img = soup.select_one(".primary-image__image")
        return img["src"] if img and img.get("src") else None
