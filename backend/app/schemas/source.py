from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SourceCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)

    @field_validator("title", "content")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class SourceResponse(BaseModel):
    id: str
    title: str
    content: str
    file_url: str | None = None
    content_type: Literal["text", "txt", "md", "pdf"]
    word_count: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
