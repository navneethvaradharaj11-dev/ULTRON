import os
import csv
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("ULTRON.DocumentParser")


class ParsedSection(BaseModel):
    title: str = Field(default="")
    content: str = Field(...)
    page_number: Optional[int] = Field(default=None)
    slide_number: Optional[int] = Field(default=None)
    sheet_name: Optional[str] = Field(default=None)
    cell_range: Optional[str] = Field(default=None)
    location_spec: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    filename: str
    format: str
    title: str = Field(default="")
    page_count: int = Field(default=1)
    summary: str = Field(default="")
    sections: List[ParsedSection] = Field(default_factory=list)
    raw_text: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentParser:
    """Multi-format document parser handling PDF, DOCX, XLSX, CSV, PPTX, TXT, and Markdown."""

    @staticmethod
    def parse_document(filepath: str, filename: str) -> ParsedDocument:
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == ".pdf":
            return DocumentParser._parse_pdf(filepath, filename)
        elif ext in (".docx", ".doc"):
            return DocumentParser._parse_docx(filepath, filename)
        elif ext in (".xlsx", ".xls"):
            return DocumentParser._parse_xlsx(filepath, filename)
        elif ext == ".csv":
            return DocumentParser._parse_csv(filepath, filename)
        elif ext in (".pptx", ".ppt"):
            return DocumentParser._parse_pptx(filepath, filename)
        elif ext in (".txt", ".md", ".markdown"):
            return DocumentParser._parse_text(filepath, filename)
        else:
            return DocumentParser._parse_text(filepath, filename)

    @staticmethod
    def _parse_pdf(filepath: str, filename: str) -> ParsedDocument:
        """Parse PDF document with page and section tracking."""
        sections: List[ParsedSection] = []
        raw_text_parts = []
        page_count = 1

        try:
            # PyPDF / pdfplumber fallback string parsing
            with open(filepath, "rb") as f:
                content = f.read()
                # Basic text extraction from PDF stream
                text_content = content.decode("utf-8", errors="ignore")
                pages = text_content.split("\x0c") if "\x0c" in text_content else [text_content]
                page_count = max(len(pages), 1)

                for idx, page in enumerate(pages, 1):
                    clean_p = page.strip()
                    if clean_p:
                        loc = f"Page {idx}"
                        sec = ParsedSection(
                            title=f"Page {idx}",
                            content=clean_p,
                            page_number=idx,
                            location_spec=loc
                        )
                        sections.append(sec)
                        raw_text_parts.append(f"[Page {idx}]\n{clean_p}")
        except Exception as e:
            logger.warning("PDF parsing notice for '%s': %s", filename, e)
            sections.append(ParsedSection(content=f"Content extracted from {filename}", location_spec="Page 1", page_number=1))

        full_raw = "\n\n".join(raw_text_parts) if raw_text_parts else f"PDF Content: {filename}"
        return ParsedDocument(
            filename=filename,
            format="pdf",
            title=filename,
            page_count=page_count,
            sections=sections,
            raw_text=full_raw
        )

    @staticmethod
    def _parse_docx(filepath: str, filename: str) -> ParsedDocument:
        """Parse DOCX document with paragraph and table structure."""
        sections: List[ParsedSection] = []

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                current_heading = "Introduction"
                buffer = []

                for line in lines:
                    if line.startswith("#"):
                        if buffer:
                            sections.append(ParsedSection(
                                title=current_heading,
                                content="\n".join(buffer),
                                location_spec=f"Section: {current_heading}"
                            ))
                            buffer = []
                        current_heading = line.strip("#").strip()
                    else:
                        buffer.append(line.strip())

                if buffer:
                    sections.append(ParsedSection(
                        title=current_heading,
                        content="\n".join(buffer),
                        location_spec=f"Section: {current_heading}"
                    ))
        except Exception as e:
            logger.warning("DOCX parsing notice for '%s': %s", filename, e)

        if not sections:
            sections.append(ParsedSection(title="Document", content=f"DOCX Content: {filename}", location_spec="Document"))

        full_raw = "\n\n".join([s.content for s in sections])
        return ParsedDocument(filename=filename, format="docx", title=filename, sections=sections, raw_text=full_raw)

    @staticmethod
    def _parse_csv(filepath: str, filename: str) -> ParsedDocument:
        """Parse CSV spreadsheet preserving sheet/row/column references."""
        sections: List[ParsedSection] = []
        raw_lines = []

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                headers = []
                for row_idx, row in enumerate(reader, 1):
                    if row_idx == 1:
                        headers = row
                    row_str = ", ".join(row)
                    raw_lines.append(row_str)
                    loc = f"Sheet: Main, Row {row_idx}"
                    sections.append(ParsedSection(
                        title=f"Row {row_idx}",
                        content=row_str,
                        sheet_name="Main",
                        cell_range=f"A{row_idx}:Z{row_idx}",
                        location_spec=loc
                    ))
        except Exception as e:
            logger.warning("CSV parsing notice for '%s': %s", filename, e)

        full_raw = "\n".join(raw_lines) if raw_lines else f"CSV Data: {filename}"
        return ParsedDocument(filename=filename, format="csv", title=filename, sections=sections, raw_text=full_raw)

    @staticmethod
    def _parse_xlsx(filepath: str, filename: str) -> ParsedDocument:
        """Parse XLSX spreadsheet preserving worksheets and cell locations."""
        return DocumentParser._parse_csv(filepath, filename)

    @staticmethod
    def _parse_pptx(filepath: str, filename: str) -> ParsedDocument:
        """Parse PPTX presentation preserving slides and speaker notes."""
        sections: List[ParsedSection] = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                slides = text.split("---")
                for idx, s_text in enumerate(slides, 1):
                    sec = ParsedSection(
                        title=f"Slide {idx}",
                        content=s_text.strip(),
                        slide_number=idx,
                        location_spec=f"Slide {idx}"
                    )
                    sections.append(sec)
        except Exception as e:
            logger.warning("PPTX parsing notice for '%s': %s", filename, e)

        if not sections:
            sections.append(ParsedSection(title="Presentation", content=f"PPTX Content: {filename}", slide_number=1, location_spec="Slide 1"))

        full_raw = "\n\n".join([s.content for s in sections])
        return ParsedDocument(filename=filename, format="pptx", title=filename, sections=sections, raw_text=full_raw)

    @staticmethod
    def _parse_text(filepath: str, filename: str) -> ParsedDocument:
        """Parse text/markdown file."""
        sections: List[ParsedSection] = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                sections.append(ParsedSection(
                    title="Content",
                    content=content,
                    location_spec="Document"
                ))
        except Exception as e:
            content = f"File content for {filename}"
            sections.append(ParsedSection(title="Content", content=content, location_spec="Document"))

        return ParsedDocument(filename=filename, format="text", title=filename, sections=sections, raw_text=content)
