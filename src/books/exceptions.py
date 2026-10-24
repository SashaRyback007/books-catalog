"""Власні винятки застосунку."""


class BookValidationError(ValueError):
    """Некоректні дані книги."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field


class CatalogImportError(Exception):
    """Помилка імпорту каталогу з CSV."""

    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line


class EmptyCatalogError(Exception):
    """Операція неможлива для порожнього каталогу."""


class ExportError(Exception):
    """Помилка експорту звіту."""


class ConfigError(Exception):
    """Некоректна конфігурація."""