import json
from unittest.mock import AsyncMock

import pytest

from books.async_catalog import AsyncCatalogService
from books.config import load_config
from books.exceptions import BookValidationError
from books.exporters import JsonBookExporter
from books.importers import import_books_csv
from books.repositories import InMemoryBookRepository
from books.services import BookCatalog

pytestmark = pytest.mark.integration


def test_configured_year_range_filters_imported_books(books_csv, monkeypatch):
    monkeypatch.setenv("BOOKS_MIN_YEAR", "1900")
    catalog = BookCatalog(InMemoryBookRepository(), load_config())
    rejected = []

    for book in import_books_csv(books_csv):
        try:
            catalog.add(book)
        except BookValidationError:
            rejected.append(book.title)

    assert rejected == ["Kobzar", "Zakhar Berkut"]
    assert [b.title for b in catalog.all()] == ["Lisova pisnia", "Tyhrolovy"]


@pytest.mark.asyncio
async def test_async_load_search_export(tmp_path):
    client = AsyncMock()
    client.fetch_books.return_value = [
        {"title": "Kobzar", "author": "Taras Shevchenko", "year": 1840, "pages": 240},
        {"title": "Zakhar Berkut", "author": "Ivan Franko", "year": 1883, "pages": 210},
    ]
    catalog = BookCatalog(InMemoryBookRepository())

    for book in await AsyncCatalogService(client).load_books("classics"):
        catalog.add(book)
    output = tmp_path / "found.json"
    JsonBookExporter().export(catalog.find_by_author("franko"), output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data == [
        {"title": "Zakhar Berkut", "author": "Ivan Franko", "year": 1883, "pages": 210}
    ]
    client.fetch_books.assert_awaited_once_with("classics")