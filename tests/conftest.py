import pytest

from books.config import ENV_MAX_YEAR, ENV_MIN_YEAR
from books.models import Book
from books.repositories import InMemoryBookRepository
from books.services import BookCatalog


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Тести не залежать від environment variables розробника."""
    monkeypatch.delenv(ENV_MIN_YEAR, raising=False)
    monkeypatch.delenv(ENV_MAX_YEAR, raising=False)


@pytest.fixture
def book_factory():
    def create(*, title="Title", author="Author", year=2000, pages=100):
        return Book(title=title, author=author, year=year, pages=pages)

    return create


@pytest.fixture
def sample_books(book_factory):
    return [
        book_factory(title="Kobzar", author="Taras Shevchenko", year=1840, pages=240),
        book_factory(title="Zakhar Berkut", author="Ivan Franko", year=1883, pages=210),
        book_factory(title="Lisova pisnia", author="Lesya Ukrainka", year=1911, pages=120),
        book_factory(title="Tyhrolovy", author="Ivan Bahrianyi", year=1944, pages=380),
    ]


@pytest.fixture
def repository(sample_books):
    repo = InMemoryBookRepository()
    for book in sample_books:
        repo.add(book)
    yield repo
    repo.clear()


@pytest.fixture
def catalog(repository):
    return BookCatalog(repository)


@pytest.fixture
def books_csv(tmp_path):
    path = tmp_path / "books.csv"
    path.write_text(
        "title,author,year,pages\n"
        "Kobzar,Taras Shevchenko,1840,240\n"
        "Zakhar Berkut,Ivan Franko,1883,210\n"
        "Lisova pisnia,Lesya Ukrainka,1911,120\n"
        "Tyhrolovy,Ivan Bahrianyi,1944,380\n",
        encoding="utf-8",
    )
    return path