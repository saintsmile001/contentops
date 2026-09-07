from app.ai.client import AIClient
from app.ai.prompts import CONTENT_DNA_INSTRUCTIONS
from app.core.config import Settings
from app.core.exceptions import AppError
from app.db.repositories.dna_repository import DNARepository
from app.db.repositories.source_repository import SourceRepository
from app.schemas.dna import ContentDNA
from app.utils.text import word_count


class DNAService:
    def __init__(self, sources: SourceRepository, dna: DNARepository, ai: AIClient, settings: Settings) -> None:
        self.sources, self.dna, self.ai, self.settings = sources, dna, ai, settings

    async def analyze(self, source_id: str, user_id: str) -> dict[str, object]:
        source = await self.sources.get_for_user(source_id, user_id)
        if word_count(str(source["content"])) < self.settings.min_source_words:
            raise AppError("SOURCE_TOO_SHORT", f"Add at least {self.settings.min_source_words} words to generate meaningful Content DNA.", 422)
        result = await self.ai.generate_structured(CONTENT_DNA_INSTRUCTIONS, str(source["content"]), ContentDNA)
        return await self.dna.upsert(source_id, result.model_dump(mode="json"))

    async def update(self, source_id: str, data: ContentDNA) -> dict[str, object]:
        return await self.dna.upsert(source_id, data.model_dump(mode="json"))
