from pydantic import BaseModel, Field


class CreatorProfileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    industry: str = Field(default="", max_length=200)
    audience: str = Field(default="", max_length=500)
    tone: str = Field(default="", max_length=200)
    default_cta: str = Field(default="", max_length=500)
    primary_platform: str = Field(default="linkedin", max_length=50)
