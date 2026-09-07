from urllib.parse import quote
from uuid import uuid4

import httpx

from app.core.config import Settings
from app.core.exceptions import AppError


class SourceRepository:
    def __init__(self, settings: Settings, access_token: str) -> None:
        self.settings = settings
        self.access_token = access_token

    @property
    def _headers(self) -> dict[str, str]:
        return {"apikey": self.settings.supabase_anon_key or "", "Authorization": f"Bearer {self.access_token}"}

    def _require_config(self) -> None:
        if not self.settings.supabase_configured:
            raise AppError("DATABASE_NOT_CONFIGURED", "Source storage is not configured on this server.", 503)

    async def create(self, user_id: str, source: dict[str, object]) -> dict[str, object]:
        self._require_config()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.settings.supabase_url.rstrip('/')}/rest/v1/source_contents",
                    headers={**self._headers, "Content-Type": "application/json", "Prefer": "return=representation"},
                    json={"user_id": user_id, **source},
                )
        except httpx.HTTPError as exc:
            raise AppError("DATABASE_UNAVAILABLE", "We couldn't save this source right now. Please try again.", 503) from exc
        if response.status_code not in {200, 201}:
            raise AppError("DATABASE_ERROR", "We couldn't save this source right now. Please try again.", 500)
        return response.json()[0]

    async def list_for_user(self, user_id: str) -> list[dict[str, object]]:
        self._require_config()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/source_contents", headers=self._headers, params={"select": "*", "user_id": f"eq.{user_id}", "order": "created_at.desc"})
        except httpx.HTTPError as exc:
            raise AppError("DATABASE_UNAVAILABLE", "We couldn't load your sources right now. Please try again.", 503) from exc
        if response.status_code != 200:
            raise AppError("DATABASE_ERROR", "We couldn't load your sources right now. Please try again.", 500)
        return response.json()

    async def get_for_user(self, source_id: str, user_id: str) -> dict[str, object]:
        self._require_config()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/source_contents", headers=self._headers, params={"select": "*", "id": f"eq.{source_id}", "user_id": f"eq.{user_id}"})
        except httpx.HTTPError as exc:
            raise AppError("DATABASE_UNAVAILABLE", "We couldn't load this source right now. Please try again.", 503) from exc
        if response.status_code != 200:
            raise AppError("DATABASE_ERROR", "We couldn't load this source right now. Please try again.", 500)
        rows = response.json()
        if not rows:
            raise AppError("SOURCE_NOT_FOUND", "This source was not found.", 404)
        return rows[0]

    async def delete_for_user(self, source_id: str, user_id: str) -> None:
        self._require_config()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(f"{self.settings.supabase_url.rstrip('/')}/rest/v1/source_contents", headers={**self._headers, "Prefer": "return=minimal"}, params={"id": f"eq.{source_id}", "user_id": f"eq.{user_id}"})
        except httpx.HTTPError as exc:
            raise AppError("DATABASE_UNAVAILABLE", "We couldn't delete this source right now. Please try again.", 503) from exc
        if response.status_code not in {200, 204}:
            raise AppError("DATABASE_ERROR", "We couldn't delete this source right now. Please try again.", 500)

    async def upload_file(self, user_id: str, filename: str, payload: bytes, mime_type: str) -> str:
        self._require_config()
        path = f"{user_id}/{uuid4()}-{quote(filename, safe='')}"
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(f"{self.settings.supabase_url.rstrip('/')}/storage/v1/object/source-files/{path}", headers={**self._headers, "Content-Type": mime_type, "x-upsert": "false"}, content=payload)
        except httpx.HTTPError as exc:
            raise AppError("STORAGE_UNAVAILABLE", "We couldn't upload this file right now. Please try again.", 503) from exc
        if response.status_code not in {200, 201}:
            raise AppError("STORAGE_ERROR", "We couldn't upload this file right now. Please try again.", 500)
        return path
