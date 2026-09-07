import httpx
from app.core.config import Settings
from app.core.exceptions import AppError
class QARepository:
 def __init__(self,settings:Settings,token:str):self.settings,self.token=settings,token
 @property
 def headers(self):return {"apikey":self.settings.supabase_anon_key or "","Authorization":f"Bearer {self.token}","Content-Type":"application/json"}
 async def upsert(self,asset_id:str,data:dict):
  if not self.settings.supabase_configured:raise AppError("DATABASE_NOT_CONFIGURED","QA storage is not configured on this server.",503)
  async with httpx.AsyncClient(timeout=10) as c:r=await c.post(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/qa_reports?on_conflict=asset_id",headers={**self.headers,"Prefer":"resolution=merge-duplicates,return=representation"},json={"asset_id":asset_id,**data})
  if r.status_code not in {200,201}:raise AppError("DATABASE_ERROR","We couldn't save this QA report.",500)
  return r.json()[0]
 async def get(self,asset_id:str):
  if not self.settings.supabase_configured:raise AppError("DATABASE_NOT_CONFIGURED","QA storage is not configured on this server.",503)
  async with httpx.AsyncClient(timeout=10) as c:r=await c.get(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/qa_reports",headers=self.headers,params={"select":"*","asset_id":f"eq.{asset_id}"})
  if r.status_code!=200:raise AppError("DATABASE_ERROR","We couldn't load this QA report.",500)
  return r.json()[0] if r.json() else None
 async def list_for_assets(self,asset_ids:list[str]):
  if not asset_ids:return []
  if not self.settings.supabase_configured:raise AppError("DATABASE_NOT_CONFIGURED","QA storage is not configured on this server.",503)
  h={"apikey":self.settings.supabase_anon_key or "","Authorization":f"Bearer {self.token}"}
  async with httpx.AsyncClient(timeout=10) as c:r=await c.get(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/qa_reports",headers=h,params={"select":"*","asset_id":f"in.({','.join(asset_ids)})"})
  if r.status_code!=200:raise AppError("DATABASE_ERROR","We couldn't load calendar QA reports.",500)
  return r.json()
