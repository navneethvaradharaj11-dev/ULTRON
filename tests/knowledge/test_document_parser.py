import os
import tempfile
import pytest
from app.knowledge.document_parser import DocumentParser, ParsedDocument


def test_parse_csv_file():
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tmp:
        tmp.write("Header1,Header2\nValue1,Value2\nValue3,Value4")
        tmp_path = tmp.name

    try:
        parsed = DocumentParser.parse_document(tmp_path, "data.csv")
        assert isinstance(parsed, ParsedDocument)
        assert parsed.format == "csv"
        assert len(parsed.sections) >= 2
        assert "Sheet: Main, Row 1" in parsed.sections[0].location_spec
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_parse_text_file():
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as tmp:
        tmp.write("This is operating system notes on CPU scheduling.")
        tmp_path = tmp.name

    try:
        parsed = DocumentParser.parse_document(tmp_path, "notes.txt")
        assert parsed.format == "text"
        assert len(parsed.sections) == 1
        assert "CPU scheduling" in parsed.raw_text
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
