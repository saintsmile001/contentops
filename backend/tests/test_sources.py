import asyncio
import unittest

from pydantic import ValidationError

from app.core.config import Settings
from app.core.exceptions import AppError
from app.schemas.source import SourceCreateRequest
from app.services.file_service import extract_file
from app.services.source_service import SourceService


class FakeSourceRepository:
    async def create(self, user_id: str, source: dict[str, object]) -> dict[str, object]:
        return {"id": "source-1", "user_id": user_id, **source}


class SourceTests(unittest.TestCase):
    def test_txt_extraction_strips_utf8_bom(self) -> None:
        source = extract_file("source.txt", "\ufeffA useful source".encode())
        self.assertEqual(source.content, "A useful source")
        self.assertEqual(source.content_type, "txt")

    def test_unsupported_file_is_rejected(self) -> None:
        with self.assertRaises(AppError) as error:
            extract_file("source.docx", b"not relevant")
        self.assertEqual(error.exception.code, "UNSUPPORTED_FILE_TYPE")

    def test_empty_source_is_rejected(self) -> None:
        with self.assertRaises(ValidationError) as error:
            SourceCreateRequest(title="Notes", content="   ")
        self.assertIn("must not be empty", str(error.exception))

    def test_text_source_is_persisted_with_word_count(self) -> None:
        service = SourceService(FakeSourceRepository(), Settings())
        source = asyncio.run(service.create_text("user-1", SourceCreateRequest(title="Notes", content="One two three")))
        self.assertEqual(source["word_count"], 3)
        self.assertEqual(source["content_type"], "text")
