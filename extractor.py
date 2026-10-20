"""
Text and structure extractor for PDF and DOCX resume documents.
Uses PyMuPDF (fitz) for PDF files and python-docx for DOCX files.
"""

import io
import re
from typing import Any, Dict, Optional, Tuple, Union

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

try:
    import docx
except ImportError:
    docx = None


class ResumeExtractor:
    """Extracts raw text and metadata from resume files."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans and standardizes extracted text.
        Removes weird non-printable characters, normalizes line breaks and whitespace.
        """
        if not text:
            return ""

        # Replace non-breaking spaces and special bullets
        text = text.replace("\u00a0", " ")
        text = text.replace("\u2022", " • ")
        text = text.replace("\u25cf", " • ")
        text = text.replace("\u25aa", " • ")
        text = text.replace("\t", " ")

        # Normalize multiple spaces per line
        text = re.sub(r"[ ]{2,}", " ", text)
        # Normalize excessive newlines (more than 2 consecutive newlines)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @classmethod
    def extract_from_pdf(
        cls, file_source: Union[str, bytes, io.BytesIO]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts text and metadata from a PDF file using PyMuPDF.

        Returns:
            Tuple of (cleaned_text, metadata_dict)
        """
        if fitz is None:
            raise ImportError(
                "PyMuPDF is not installed. Please install with `pip install PyMuPDF`."
            )

        doc = None
        try:
            if isinstance(file_source, str):
                doc = fitz.open(file_source)
            elif isinstance(file_source, bytes):
                doc = fitz.open(stream=file_source, filetype="pdf")
            elif hasattr(file_source, "read"):
                # Stream / UploadedFile
                content = file_source.read()
                doc = fitz.open(stream=content, filetype="pdf")
            else:
                raise ValueError("Unsupported PDF file source type.")

            if doc.is_encrypted:
                raise ValueError(
                    "This PDF is password-protected or encrypted. Please upload an unprotected file."
                )

            total_pages = len(doc)
            extracted_pages = []

            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                page_text = page.get_text("text") or ""
                extracted_pages.append(page_text)

            full_text = "\n\n".join(extracted_pages)
            cleaned = cls.clean_text(full_text)

            # Check if this might be a scanned image-only PDF
            is_scanned_warning = False
            if total_pages > 0 and len(cleaned) < (total_pages * 40):
                is_scanned_warning = True

            meta = {
                "file_type": "pdf",
                "page_count": total_pages,
                "character_count": len(cleaned),
                "word_count": len(cleaned.split()),
                "is_scanned_warning": is_scanned_warning,
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
            }

            return cleaned, meta

        finally:
            if doc is not None:
                doc.close()

    @classmethod
    def extract_from_docx(
        cls, file_source: Union[str, bytes, io.BytesIO]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts text from a DOCX file using python-docx.
        Extracts from paragraphs and tables.

        Returns:
            Tuple of (cleaned_text, metadata_dict)
        """
        if docx is None:
            raise ImportError(
                "python-docx is not installed. Please install with `pip install python-docx`."
            )

        if isinstance(file_source, bytes):
            file_stream = io.BytesIO(file_source)
        elif hasattr(file_source, "read"):
            file_stream = file_source
        elif isinstance(file_source, str):
            file_stream = file_source
        else:
            raise ValueError("Unsupported DOCX file source type.")

        doc = docx.Document(file_stream)
        text_parts = []

        # 1. Paragraphs
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                text_parts.append(text)

        # 2. Tables (resumes often put contact details or skills in tables)
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    text_parts.append(" | ".join(row_cells))

        full_text = "\n".join(text_parts)
        cleaned = cls.clean_text(full_text)

        word_count = len(cleaned.split())
        # Approximate page count (standard 350-450 words per resume page)
        estimated_pages = max(1, round(word_count / 400)) if word_count > 0 else 0

        meta = {
            "file_type": "docx",
            "page_count": estimated_pages,
            "character_count": len(cleaned),
            "word_count": word_count,
            "paragraph_count": len(doc.paragraphs),
            "table_count": len(doc.tables),
            "is_scanned_warning": False,
        }

        return cleaned, meta

    @classmethod
    def extract_text(
        cls, file_source: Any, filename: str = ""
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Dispatches extraction based on file extension / filename.
        """
        fn = filename.lower()
        if fn.endswith(".pdf"):
            return cls.extract_from_pdf(file_source)
        elif fn.endswith(".docx"):
            return cls.extract_from_docx(file_source)
        else:
            # Fallback attempt by sniffing or default to PDF
            try:
                return cls.extract_from_pdf(file_source)
            except Exception:
                try:
                    if hasattr(file_source, "seek"):
                        file_source.seek(0)
                    return cls.extract_from_docx(file_source)
                except Exception:
                    raise ValueError(
                        "Unsupported file format. Please upload a .pdf or .docx resume file."
                    )
