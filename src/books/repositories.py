"""Репозиторії (fake in-memory реалізація)."""

from books.models import Book


class InMemoryBookRepository:
    def __init__(self) -> None:
        self._books: list[Book] = []

    def add(self, book: Book) -> None:
        self._books.append(book)

    def list_all(self) -> list[Book]:
        return list(self._books)

    def clear(self) -> None:
        self._books.clear()