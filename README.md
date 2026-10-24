# Books Catalog: лабораторна робота №6 (варіант 2)

Система обліку книг із повним набором автоматизованих тестів (pytest).

## Встановлення і запуск
```
python -m pip install -e ".[dev]"
pytest
```
Команда запускає 86 тестів і формує звіт coverage (з branch coverage) та `htmlcov/index.html`.

## Структура
- `src/books/` — production-код
- `tests/unit/` — unit tests
- `tests/integration/` — integration tests