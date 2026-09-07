from dataclasses import dataclass
from pathlib import Path

from app.core.exceptions import AppError


SUPPORTED_EXTENSIONS = {".txt": "txt", ".md": "md", ".pdf": "pdf"}


@dataclass(frozen=True)
class ExtractedFile:
    filename: str
    content: str
    content_type: str


def extract_file(filename: str, payload: bytes) -> ExtractedFile:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise AppError("UNSUPPORTED_FILE_TYPE", "Upload a TXT, Markdown, or PDF file.", 422)
    if not payload:
        raise AppError("SOURCE_EMPTY", "The uploaded file is empty.", 422)

    if extension in {".txt", ".md"}:
        try:
            content = payload.decode("utf-8-sig").strip()
        except UnicodeDecodeError as exc:
            raise AppError("FILE_EXTRACTION_FAILED", "We couldn't read this text file. Please save it as UTF-8.", 422) from exc
    else:
        try:
            from pypdf import PdfReader

            from io import BytesIO

            reader = PdfReader(BytesIO(payload))
            content = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except ImportError as exc:
            raise AppError("FILE_EXTRACTION_FAILED", "PDF extraction is unavailable until the server dependencies are installed.", 503) from exc
        except Exception as exc:
            raise AppError("FILE_EXTRACTION_FAILED", "We couldn't extract readable text from this PDF.", 422) from exc

    if not content:
        raise AppError("FILE_EXTRACTION_FAILED", "No readable text was found in this file.", 422)
    return ExtractedFile(filename=filename, content=content, content_type=SUPPORTED_EXTENSIONS[extension])
