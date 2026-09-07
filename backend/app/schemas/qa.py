from typing import Literal
from pydantic import BaseModel, Field

QAStatus=Literal["PASS","WARNING","FAIL"]
class SupportedClaim(BaseModel):
 claim:str
 evidence:str
class QAReport(BaseModel):
 faithfulness_score:int=Field(ge=0,le=100)
 source_coverage_score:int=Field(ge=0,le=100)
 brand_alignment_score:int=Field(ge=0,le=100)
 unsupported_claims:list[str]=Field(default_factory=list)
 supported_claims:list[SupportedClaim]=Field(default_factory=list)
 issues:list[str]=Field(default_factory=list)
 recommendations:list[str]=Field(default_factory=list)
 status:QAStatus
