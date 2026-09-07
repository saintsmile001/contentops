import httpx
from app.core.config import Settings
from app.core.exceptions import AppError

class CampaignRepository:
    def __init__(self, settings: Settings, token: str) -> None:
        self.settings, self.token = settings, token

    @property
    def headers(self):
        return {"apikey": self.settings.supabase_anon_key or "", "Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def ready(self):
        if not self.settings.supabase_configured:
            raise AppError("DATABASE_NOT_CONFIGURED", "Campaign storage is not configured on this server.", 503)

    async def request(self, method: str, table: str, **kwargs):
        self.ready()
        headers = kwargs.pop("headers", self.headers)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.request(method, f"{self.settings.supabase_url.rstrip('/')}/rest/v1/{table}", headers=headers, **kwargs)
        if response.status_code >= 400:
            raise AppError("DATABASE_ERROR", "We couldn't complete this campaign action. Please try again.", 500)
        return response.json() if response.content else None

    async def create(self, user_id: str, data: dict):
        rows = await self.request("POST", "campaigns", json={"user_id": user_id, **data}, headers={**self.headers, "Prefer": "return=representation"})
        if not rows:
            raise AppError("DATABASE_ERROR", "We couldn't create this campaign.", 500)
        return rows[0]

    async def get(self, campaign_id: str, user_id: str):
        rows = await self.request("GET", "campaigns", params={"select": "*", "id": f"eq.{campaign_id}", "user_id": f"eq.{user_id}"})
        if not rows:
            raise AppError("CAMPAIGN_NOT_FOUND", "This campaign was not found.", 404)
        return rows[0]

    async def get_by_id(self, campaign_id: str):
        """Get campaign without user_id check — for background tasks where ownership was already verified."""
        rows = await self.request("GET", "campaigns", params={"select": "*", "id": f"eq.{campaign_id}"})
        if not rows:
            raise AppError("CAMPAIGN_NOT_FOUND", "This campaign was not found.", 404)
        return rows[0]

    async def list(self, user_id: str):
        return await self.request("GET", "campaigns", params={"select": "*", "user_id": f"eq.{user_id}", "order": "created_at.desc"})

    async def update_status(self, campaign_id: str, status: str):
        await self.request("PATCH", f"campaigns?id=eq.{campaign_id}", json={"status": status})

    async def delete(self, campaign_id: str, user_id: str):
        await self.get(campaign_id, user_id)
        await self.request("DELETE", f"campaigns?id=eq.{campaign_id}&user_id=eq.{user_id}", headers={**self.headers, "Prefer": "return=minimal"})

    async def save_strategy(self, campaign_id: str, strategy: dict):
        rows = await self.request("POST", "campaign_strategies?on_conflict=campaign_id", json={"campaign_id": campaign_id, "strategy": strategy}, headers={**self.headers, "Prefer": "resolution=merge-duplicates,return=representation"})
        if not rows:
            raise AppError("DATABASE_ERROR", "We couldn't save the campaign strategy.", 500)
        return rows[0]

    async def get_strategy(self, campaign_id: str):
        rows = await self.request("GET", "campaign_strategies", params={"select": "strategy", "campaign_id": f"eq.{campaign_id}"})
        if not rows:
            raise AppError("STRATEGY_NOT_FOUND", "Generate the campaign strategy first.", 404)
        return rows[0]["strategy"]
