"""Async-доступ до зовнішнього каталогу."""

from books.models import Book


class AsyncCatalogService:
    def __init__(self, client) -> None:
        self._client = client

    async def load_books(self, query: str) -> list[Book]:
        items = await self._client.fetch_books(query)
        return [Book(**item) for item in items]