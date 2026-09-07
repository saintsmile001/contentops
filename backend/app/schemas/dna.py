from pydantic import BaseModel, Field


class Claim(BaseModel):
    claim: str
    evidence: str


class Statistic(BaseModel):
    statistic: str
    context: str


class ContentDNA(BaseModel):
    title: str
    main_thesis: str
    target_audience: str
    content_pillars: list[str] = Field(default_factory=list)
    key_points: list[str] = Field(default_factory=list)
    stories: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    statistics: list[Statistic] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    tone: str
    cta: str
    summary: str
