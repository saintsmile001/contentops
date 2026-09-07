from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

AssetStatus=Literal["GENERATING","READY","WARNING","FAILED"]
class SocialAsset(BaseModel):
 platform: Literal["linkedin","x","instagram","threads"]
 content_type: str
 title: str
 hook: str
 content: str
 cta: str
 hashtags: list[str]=Field(default_factory=list)
class SEOAsset(BaseModel):
 seo_title:str; meta_description:str; primary_keyword:str; secondary_keywords:list[str]=Field(default_factory=list); search_intent:str; content_angle:str; url_slug:str
class AssetResponse(SocialAsset):
 id:str; campaign_id:str; status:AssetStatus; scheduled_for:datetime|None=None
class AssetUpdateRequest(BaseModel):
 title:str=Field(min_length=1,max_length=200)
 hook:str=Field(default="",max_length=500)
 content:str=Field(min_length=1)
 cta:str=Field(default="",max_length=500)
 hashtags:list[str]=Field(default_factory=list)
class RegenerateRequest(BaseModel):
 instruction:str|None=Field(default=None,max_length=500)
