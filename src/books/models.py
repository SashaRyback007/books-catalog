"""Доменна модель Book."""

from dataclasses import dataclass

from books.exceptions import BookValidationError

MIN_YEAR = 1450
MAX_YEAR = 2100


def _require_text(field: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise BookValidationError(field, "must be a non-empty string")


def _require_int(field: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise BookValidationError(field, "must be an integer")


@dataclass(frozen=True, slots=True)
class Book:
    title: str
    author: str
    year: int
    pages: int

    def __post_init__(self) -> None:
        _require_text("title", self.title)
        _require_text("author", self.author)
        _require_int("year", self.year)
        if not MIN_YEAR <= self.year <= MAX_YEAR:
            raise BookValidationError(
                "year",
                f"must be between {MIN_YEAR} and {MAX_YEAR}",
            )
        _require_int("pages", self.pages)
        if self.pages <= 0:
            raise BookValidationError("pages", "must be positive")