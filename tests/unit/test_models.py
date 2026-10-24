from dataclasses import FrozenInstanceError

import pytest

from books.exceptions import BookValidationError
from books.models import MAX_YEAR, MIN_YEAR, Book


def test_book_creation_with_valid_data():
    book = Book("Kobzar", "Taras Shevchenko", 1840, 240)

    assert book.title == "Kobzar"
    assert book.author == "Taras Shevchenko"
    assert book.year == 1840
    assert book.pages == 240


@pytest.mark.parametrize(
    "year",
    [
        pytest.param(MIN_YEAR, id="min-year"),
        pytest.param(MIN_YEAR + 1, id="min-year-plus-one"),
        pytest.param(2000, id="normal"),
        pytest.param(MAX_YEAR - 1, id="max-year-minus-one"),
        pytest.param(MAX_YEAR, id="max-year"),
    ],
)
def test_valid_year_boundaries(book_factory, year):
    assert book_factory(year=year).year == year


@pytest.mark.parametrize("year", [MIN_YEAR - 1, MAX_YEAR + 1, 0, -5])
def test_invalid_year_is_rejected(book_factory, year):
    with pytest.raises(BookValidationError, match="year") as exc_info:
        book_factory(year=year)

    assert exc_info.value.field == "year"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("title", "   "),
        ("author", ""),
        ("author", "  "),
        ("pages", 0),
        ("pages", -10),
    ],
)
def test_invalid_text_or_pages_is_rejected(book_factory, field, value):
    with pytest.raises(BookValidationError) as exc_info:
        book_factory(**{field: value})

    assert exc_info.value.field == field


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("year", "1999"),
        ("year", 1999.5),
        ("pages", "100"),
        ("pages", True),
    ],
)
def test_wrong_type_is_rejected(book_factory, field, value):
    with pytest.raises(BookValidationError, match="integer") as exc_info:
        book_factory(**{field: value})

    assert exc_info.value.field == field


def test_minimum_valid_pages(book_factory):
    assert book_factory(pages=1).pages == 1


def test_book_is_immutable(book_factory):
    book = book_factory()

    with pytest.raises(FrozenInstanceError):
        book.title = "Other"