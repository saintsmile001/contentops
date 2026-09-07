import httpx
from app.core.config import Settings
from app.core.exceptions import AppError


class ProfileRepository:
    def __init__(self, settings: Settings, token: str) -> None:
        self.settings, self.token = settings, token

    @property
    def _headers(self) -> dict[str, str]:
        return {"apikey": self.settings.supabase_anon_key or "", "Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def _require(self) -> None:
        if not self.settings.supabase_configured:
            raise AppError("DATABASE_NOT_CONFIGURED", "Profile storage is not configured on this server.", 503)

    async def upsert(self, user_id: str, data: dict) -> dict:
        self._require()
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                f"{self.settings.supabase_url.rstrip('/')}/rest/v1/creator_profiles?on_conflict=user_id",
                headers={**self._headers, "Prefer": "resolution=merge-duplicates,return=representation"},
                json={"user_id": user_id, **data},
            )
        if r.status_code not in {200, 201}:
            raise AppError("DATABASE_ERROR", "We couldn't save your creator profile right now.", 500)
        rows = r.json()
        if not rows:
            raise AppError("DATABASE_ERROR", "We couldn't save your creator profile right now.", 500)
        return rows[0]

    async def get(self, user_id: str) -> dict | None:
        self._require()
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(
                f"{self.settings.supabase_url.rstrip('/')}/rest/v1/creator_profiles",
                headers=self._headers,
                params={"select": "*", "user_id": f"eq.{user_id}"},
            )
        if r.status_code != 200:
            raise AppError("DATABASE_ERROR", "We couldn't load your creator profile right now.", 500)
        rows = r.json()
        return rows[0] if rows else None
