import httpx

from app.core.config import Settings


async def check_database_connection(settings: Settings) -> bool | None:
    """Return None when Supabase is not configured, otherwise probe its REST API."""
    if not settings.supabase_configured:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.supabase_url.rstrip('/')}/rest/v1/",
                headers={"apikey": settings.supabase_anon_key or ""},
            )
        return response.status_code < 500
    except httpx.HTTPError:
        return False

