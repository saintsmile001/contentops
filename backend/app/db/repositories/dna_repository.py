import httpx

from app.core.config import Settings
from app.core.exceptions import AppError


class DNARepository:
    def __init__(self, settings: Settings, token: str) -> None:
        self.settings, self.token = settings, token

    async def upsert(self, source_id: str, data: dict[str, object]) -> dict[str, object]:
        if not self.settings.supabase_configured: raise AppError("DATABASE_NOT_CONFIGURED", "Source storage is not configured on this server.", 503)
        headers = {"apikey": self.settings.supabase_anon_key or "", "Authorization": f"Bearer {self.token}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=representation"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_dna?on_conflict=source_id", headers=headers, json={"source_id": source_id, **data})
        if response.status_code not in {200,201}: raise AppError("DATABASE_ERROR", "We couldn't save Content DNA right now. Please try again.", 500)
        return response.json()[0]

    async def get(self, source_id: str) -> dict[str, object]:
        if not self.settings.supabase_configured: raise AppError("DATABASE_NOT_CONFIGURED", "Source storage is not configured on this server.", 503)
        headers = {"apikey": self.settings.supabase_anon_key or "", "Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_dna", headers=headers, params={"select":"*","source_id":f"eq.{source_id}"})
        if response.status_code != 200: raise AppError("DATABASE_ERROR", "We couldn't load Content DNA right now. Please try again.", 500)
        rows=response.json()
        if not rows: raise AppError("DNA_NOT_FOUND", "Analyze this source to create Content DNA.", 404)
        return rows[0]

    async def exists(self, source_id: str) -> bool:
        if not self.settings.supabase_configured: raise AppError("DATABASE_NOT_CONFIGURED", "Source storage is not configured on this server.", 503)
        headers = {"apikey": self.settings.supabase_anon_key or "", "Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_dna", headers=headers, params={"select":"id","source_id":f"eq.{source_id}","limit":"1"})
        if response.status_code != 200: raise AppError("DATABASE_ERROR", "We couldn't check Content DNA right now. Please try again.", 500)
        return bool(response.json())
