"""JSON export (атомарний запис)."""

import json
import os
from dataclasses import asdict
from pathlib import Path

from books.models import Book


class JsonBookExporter:
    def export(self, books: list[Book], path: str | Path) -> None:
        path = Path(path)
        temporary = path.with_name(path.name + ".tmp")
        payload = json.dumps(
            [asdict(book) for book in books],
            ensure_ascii=False,
            indent=2,
        )
        try:
            temporary.write_text(payload, encoding="utf-8")
            os.replace(temporary, path)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise