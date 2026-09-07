from app.ai.client import AIClient
from app.ai.qa import QA_INSTRUCTIONS
from app.db.repositories.asset_repository import AssetRepository
from app.db.repositories.dna_repository import DNARepository
from app.db.repositories.qa_repository import QARepository
from app.schemas.qa import QAReport
class QAService:
 def __init__(self,assets:AssetRepository,dna:DNARepository,reports:QARepository,ai:AIClient):self.assets,self.dna,self.reports,self.ai=assets,dna,reports,ai
 async def run(self,asset_id:str,source_id:str):
  asset=await self.assets.get(asset_id); dna=await self.dna.get(source_id)
  report=await self.ai.generate_structured(QA_INSTRUCTIONS,str({"content_dna":dna,"asset":asset}),QAReport)
  return await self.reports.upsert(asset_id,report.model_dump(mode="json"))
