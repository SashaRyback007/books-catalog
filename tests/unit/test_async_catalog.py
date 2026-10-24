from unittest.mock import AsyncMock

import pytest

from books.async_catalog import AsyncCatalogService
from books.exceptions import BookValidationError

ITEM = {"title": "Kobzar", "author": "Taras Shevchenko", "year": 1840, "pages": 240}


@pytest.mark.asyncio
async def test_load_books_returns_book_objects():
    client = AsyncMock()
    client.fetch_books.return_value = [ITEM]

    books = await AsyncCatalogService(client).load_books("kobzar")

    assert len(books) == 1
    assert books[0].title == "Kobzar"
    client.fetch_books.assert_awaited_once_with("kobzar")


@pytest.mark.asyncio
async def test_load_books_empty_response():
    client = AsyncMock()
    client.fetch_books.return_value = []

    assert await AsyncCatalogService(client).load_books("none") == []


@pytest.mark.asyncio
async def test_load_books_network_failure_propagates():
    client = AsyncMock()
    client.fetch_books.side_effect = ConnectionError("Network error")

    with pytest.raises(ConnectionError, match="Network"):
        await AsyncCatalogService(client).load_books("any")


@pytest.mark.asyncio
async def test_load_books_invalid_item_raises_validation_error():
    client = AsyncMock()
    client.fetch_books.return_value = [{**ITEM, "pages": 0}]

    with pytest.raises(BookValidationError, match="pages"):
        await AsyncCatalogService(client).load_books("bad")