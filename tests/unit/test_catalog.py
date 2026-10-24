import pytest

from books.config import CatalogConfig
from books.exceptions import BookValidationError, EmptyCatalogError
from books.repositories import InMemoryBookRepository
from books.services import BookCatalog


def test_empty_catalog_returns_empty_list():
    catalog = BookCatalog(InMemoryBookRepository())

    assert catalog.all() == []


def test_add_book_stores_it(catalog, book_factory):
    book = book_factory(title="New book")

    catalog.add(book)

    assert len(catalog.all()) == 5
    assert book in catalog.all()


def test_find_by_author_is_case_insensitive(catalog):
    result = catalog.find_by_author("SHEVCHENKO")

    assert [book.title for book in result] == ["Kobzar"]


def test_find_by_author_partial_match_returns_several(catalog):
    result = catalog.find_by_author("ivan")

    assert {book.title for book in result} == {"Zakhar Berkut", "Tyhrolovy"}


def test_find_by_title(catalog):
    result = catalog.find_by_title("pisnia")

    assert [book.author for book in result] == ["Lesya Ukrainka"]


@pytest.mark.parametrize(
    ("method", "query"),
    [
        ("find_by_author", "nobody"),
        ("find_by_title", "nothing"),
    ],
)
def test_search_without_match_returns_empty_list(catalog, method, query):
    assert getattr(catalog, method)(query) == []


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        pytest.param(1840, 1840, ["Kobzar"], id="inclusive-single-year"),
        pytest.param(1800, 1900, ["Kobzar", "Zakhar Berkut"], id="range"),
        pytest.param(1945, 2000, [], id="no-results"),
        pytest.param(
            1000,
            3000,
            ["Kobzar", "Zakhar Berkut", "Lisova pisnia", "Tyhrolovy"],
            id="all",
        ),
    ],
)
def test_filter_by_year(catalog, start, end, expected):
    result = catalog.filter_by_year(start, end)

    assert [book.title for book in result] == expected


def test_filter_by_year_with_reversed_range_raises(catalog):
    with pytest.raises(ValueError, match="start"):
        catalog.filter_by_year(1950, 1900)


def test_largest_book_by_pages(catalog):
    assert catalog.largest_by_pages().title == "Tyhrolovy"


def test_average_pages(catalog):
    assert catalog.average_pages() == pytest.approx(237.5)


@pytest.mark.parametrize("method", ["largest_by_pages", "average_pages"])
def test_empty_catalog_statistics_raise(method):
    catalog = BookCatalog(InMemoryBookRepository())

    with pytest.raises(EmptyCatalogError, match="empty"):
        getattr(catalog, method)()


def test_add_outside_configured_range_is_rejected(book_factory):
    repository = InMemoryBookRepository()
    catalog = BookCatalog(repository, CatalogConfig(1900, 2000))

    with pytest.raises(BookValidationError, match="between"):
        catalog.add(book_factory(year=1840))

    assert repository.list_all() == []


@pytest.mark.parametrize("year", [1900, 2000])
def test_add_on_configured_boundaries_is_accepted(book_factory, year):
    repository = InMemoryBookRepository()
    catalog = BookCatalog(repository, CatalogConfig(1900, 2000))

    catalog.add(book_factory(year=year))

    assert len(repository.list_all()) == 1