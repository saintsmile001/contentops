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
            async with httpx.AsyncClient(timeout=15.0) as client:
                # 1. Fetch source to verify existence and check for attached storage file
                source_res = await client.get(
                    f"{self.settings.supabase_url.rstrip('/')}/rest/v1/source_contents",
                    headers=self._headers,
                    params={"select": "*", "id": f"eq.{source_id}", "user_id": f"eq.{user_id}"}
                )
                source_rows = source_res.json() if source_res.status_code == 200 else []
                if not source_rows:
                    raise AppError("SOURCE_NOT_FOUND", "This source was not found.", 404)

                source = source_rows[0]

                # 2. Clear content_dna dependent records
                await client.delete(
                    f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_dna",
                    headers=self._headers,
                    params={"source_id": f"eq.{source_id}"}
                )

                # 3. Clear dependent campaigns and their sub-assets/strategies
                campaigns_res = await client.get(
                    f"{self.settings.supabase_url.rstrip('/')}/rest/v1/campaigns",
                    headers=self._headers,
                    params={"select": "id", "source_id": f"eq.{source_id}", "user_id": f"eq.{user_id}"}
                )
                c_rows = campaigns_res.json() if campaigns_res.status_code == 200 else []
                for c in c_rows:
                    c_id = c.get("id")
                    if c_id:
                        await client.delete(
                            f"{self.settings.supabase_url.rstrip('/')}/rest/v1/campaign_strategies",
                            headers=self._headers,
                            params={"campaign_id": f"eq.{c_id}"}
                        )
                        assets_res = await client.get(
                            f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_assets",
                            headers=self._headers,
                            params={"select": "id", "campaign_id": f"eq.{c_id}"}
                        )
                        asset_rows = assets_res.json() if assets_res.status_code == 200 else []
                        for a in asset_rows:
                            await client.delete(
                                f"{self.settings.supabase_url.rstrip('/')}/rest/v1/qa_reports",
                                headers=self._headers,
                                params={"asset_id": f"eq.{a['id']}"}
                            )
                        await client.delete(
                            f"{self.settings.supabase_url.rstrip('/')}/rest/v1/content_assets",
                            headers=self._headers,
                            params={"campaign_id": f"eq.{c_id}"}
                        )
                        await client.delete(
                            f"{self.settings.supabase_url.rstrip('/')}/rest/v1/campaigns",
                            headers=self._headers,
                            params={"id": f"eq.{c_id}", "user_id": f"eq.{user_id}"}
                        )

                # 4. If a uploaded file URL exists, delete from storage
                if source.get("file_url"):
                    file_path = source["file_url"]
                    await client.delete(
                        f"{self.settings.supabase_url.rstrip('/')}/storage/v1/object/source-files/{file_path}",
                        headers=self._headers
                    )

                # 5. Delete source_contents row
                response = await client.delete(
                    f"{self.settings.supabase_url.rstrip('/')}/rest/v1/source_contents",
                    headers={**self._headers, "Prefer": "return=minimal"},
                    params={"id": f"eq.{source_id}", "user_id": f"eq.{user_id}"}
                )
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
