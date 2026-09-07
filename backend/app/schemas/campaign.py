from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Platform = Literal["linkedin", "x", "instagram", "threads"]
CampaignStatus = Literal["DRAFT", "GENERATING", "COMPLETED", "FAILED"]

class CampaignCreateRequest(BaseModel):
    source_id: str
    name: str = Field(min_length=1, max_length=200)
    duration: int = Field(default=7, ge=7, le=7)
    platforms: list[Platform] = Field(default_factory=lambda: ["linkedin", "x", "instagram"])

class StrategyDay(BaseModel):
    day: int = Field(ge=1, le=7)
    platform: Platform
    content_type: str
    angle: str
    hook: str
    objective: str

class CampaignStrategy(BaseModel):
    duration: int = 7
    days: list[StrategyDay] = Field(min_length=7, max_length=7)

class CampaignResponse(BaseModel):
    id: str
    source_id: str
    name: str
    duration: int
    status: CampaignStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None
