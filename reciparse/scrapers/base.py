"""Base scraper interface for all recipe site scrapers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RecipeData:
    """Normalized recipe data structure."""

    title: str
    url: str
    ingredients: List[str] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    total_time: Optional[str] = None
    servings: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    source: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert recipe data to a plain dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "total_time": self.total_time,
            "servings": self.servings,
            "image_url": self.image_url,
            "tags": self.tags,
            "source": self.source,
        }


class BaseScraper(ABC):
    """Abstract base class for recipe scrapers."""

    SUPPORTED_DOMAINS: List[str] = []

    def __init__(self, url: str) -> None:
        self.url = url

    @classmethod
    def supports(cls, url: str) -> bool:
        """Return True if this scraper handles the given URL."""
        return any(domain in url for domain in cls.SUPPORTED_DOMAINS)

    @abstractmethod
    def scrape(self) -> RecipeData:
        """Fetch and parse the recipe, returning a RecipeData instance."""
        raise NotImplementedError

    def _clean_text(self, text: str) -> str:
        """Strip and normalize whitespace from a string."""
        return " ".join(text.split()).strip()
