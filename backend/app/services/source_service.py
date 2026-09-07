from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import AppError
from app.db.repositories.source_repository import SourceRepository
from app.schemas.source import SourceCreateRequest
from app.services.file_service import extract_file
from app.utils.text import word_count


class SourceService:
    def __init__(self, repository: SourceRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    async def create_text(self, user_id: str, request: SourceCreateRequest) -> dict[str, object]:
        return await self._persist(user_id, request.title, request.content, "text")

    async def create_file(self, user_id: str, filename: str, payload: bytes, mime_type: str) -> dict[str, object]:
        if len(payload) > self.settings.max_source_size_mb * 1024 * 1024:
            raise AppError("FILE_TOO_LARGE", f"Files must be smaller than {self.settings.max_source_size_mb} MB.", 422)
        extracted = extract_file(filename, payload)
        file_url = await self.repository.upload_file(user_id, filename, payload, mime_type)
        return await self._persist(user_id, Path(filename).stem or filename, extracted.content, extracted.content_type, file_url)

    async def _persist(self, user_id: str, title: str, content: str, content_type: str, file_url: str | None = None) -> dict[str, object]:
        count = word_count(content)
        if count == 0:
            raise AppError("SOURCE_EMPTY", "Add content before saving your source.", 422)
        if count > self.settings.max_source_words:
            raise AppError("SOURCE_TOO_LONG", f"Sources must contain at most {self.settings.max_source_words:,} words.", 422)
        return await self.repository.create(user_id, {"title": title.strip(), "content": content.strip(), "file_url": file_url, "content_type": content_type, "word_count": count})
