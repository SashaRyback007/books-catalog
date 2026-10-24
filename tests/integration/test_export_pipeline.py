import json

import pytest

from books.exceptions import ExportError
from books.exporters import JsonBookExporter
from books.services import ReportService

pytestmark = pytest.mark.integration


def test_report_service_with_real_exporter(repository, tmp_path):
    output = tmp_path / "report.json"

    count = ReportService(repository, JsonBookExporter()).publish(output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert count == 4
    assert [item["title"] for item in data][0] == "Kobzar"


def test_report_service_fails_when_directory_missing(repository, tmp_path):
    output = tmp_path / "no_such_dir" / "report.json"

    with pytest.raises(ExportError) as exc_info:
        ReportService(repository, JsonBookExporter()).publish(output)

    assert isinstance(exc_info.value.__cause__, OSError)
    assert not output.exists()