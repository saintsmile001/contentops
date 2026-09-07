import httpx
from app.core.config import Settings
from app.core.exceptions import AppError
class AssetRepository:
 def __init__(self,settings:Settings,token:str): self.settings,self.token=settings,token
 async def create(self,campaign_id:str,data:dict):
  if not self.settings.supabase_configured: raise AppError("DATABASE_NOT_CONFIGURED","Asset storage is not configured on this server.",503)
  h={"apikey":self.settings.supabase_anon_key or "","Authorization":f"Bearer {self.token}","Content-Type":"application/json","Prefer":"return=representation"}
  async with httpx.AsyncClient(timeout=10) as c:r=await c.post(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_assets",headers=h,json={"campaign_id":campaign_id,"status":"READY",**data})
  if r.status_code not in {200,201}: raise AppError("DATABASE_ERROR","We couldn't save this asset right now.",500)
  return r.json()[0]
 async def list(self,campaign_id:str):
  h={"apikey":self.settings.supabase_anon_key or "","Authorization":f"Bearer {self.token}"}
  async with httpx.AsyncClient(timeout=10) as c:r=await c.get(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_assets",headers=h,params={"select":"*","campaign_id":f"eq.{campaign_id}","order":"created_at.asc"})
  if r.status_code!=200: raise AppError("DATABASE_ERROR","We couldn't load campaign assets.",500)
  return r.json()
 async def get(self,asset_id:str):
  h={"apikey":self.settings.supabase_anon_key or "","Authorization":f"Bearer {self.token}"}
  async with httpx.AsyncClient(timeout=10) as c:r=await c.get(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_assets",headers=h,params={"select":"*","id":f"eq.{asset_id}"})
  if r.status_code!=200:raise AppError("DATABASE_ERROR","We couldn't load this asset.",500)
  rows=r.json()
  if not rows:raise AppError("ASSET_NOT_FOUND","This asset was not found.",404)
  return rows[0]
 async def schedule(self,asset_id:str,scheduled_for:str):
  h={"apikey":self.settings.supabase_anon_key or "","Authorization":f"Bearer {self.token}","Content-Type":"application/json","Prefer":"return=representation"}
  async with httpx.AsyncClient(timeout=10) as c:r=await c.patch(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_assets?id=eq.{asset_id}",headers=h,json={"scheduled_for":scheduled_for})
  if r.status_code!=200:raise AppError("DATABASE_ERROR","We couldn't schedule this asset.",500)
  return r.json()[0]
 async def update(self,asset_id:str,data:dict):
  h={"apikey":self.settings.supabase_anon_key or "","Authorization":f"Bearer {self.token}","Content-Type":"application/json","Prefer":"return=representation"}
  async with httpx.AsyncClient(timeout=10) as c:r=await c.patch(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_assets?id=eq.{asset_id}",headers=h,json=data)
  if r.status_code!=200:raise AppError("DATABASE_ERROR","We couldn't save this asset.",500)
  return r.json()[0]
 async def delete_for_campaign(self,campaign_id:str):
  h={"apikey":self.settings.supabase_anon_key or "","Authorization":f"Bearer {self.token}","Prefer":"return=minimal"}
  async with httpx.AsyncClient(timeout=10) as c:r=await c.delete(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_assets",headers=h,params={"campaign_id":f"eq.{campaign_id}"})
  if r.status_code not in {200,204}:raise AppError("DATABASE_ERROR","We couldn't reset campaign assets.",500)
