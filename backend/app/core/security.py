import asyncio
from dataclasses import dataclass
from time import monotonic
from typing import Annotated

import httpx
from fastapi import Depends, Header

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str | None = None


_verified_tokens: dict[str, tuple[AuthenticatedUser, float]] = {}
_TOKEN_CACHE_SECONDS = 60.0


async def get_current_user(
    authorization: str | None = Header(default=None),
    settings: Annotated[Settings, Depends(get_settings)] = None,
) -> AuthenticatedUser:
    """Validate Supabase-issued bearer tokens server-side via the Auth API."""
    settings = settings or get_settings()
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError("UNAUTHENTICATED", "Authentication is required.", 401)
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise AppError("UNAUTHENTICATED", "Authentication is required.", 401)

    cached = _verified_tokens.get(token)
    if cached and cached[1] > monotonic():
        return cached[0]
    if not settings.supabase_configured:
        raise AppError("AUTH_NOT_CONFIGURED", "Authentication is not configured on this server.", 503)

    response: httpx.Response | None = None
    last_error: httpx.HTTPError | None = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(
                    f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                    headers={"apikey": settings.supabase_anon_key or "", "Authorization": f"Bearer {token}"},
                )
            if response.status_code < 500:
                break
        except httpx.HTTPError as exc:
            last_error = exc
        if attempt < 2:
            await asyncio.sleep(0.25 * (attempt + 1))

    if response is None or response.status_code >= 500:
        raise AppError("AUTH_UNAVAILABLE", "Authentication could not be verified. Please try again.", 503) from last_error

    if response.status_code != 200:
        raise AppError("UNAUTHENTICATED", "Your session is invalid or has expired.", 401)
    payload = response.json()
    user_id = payload.get("id")
    if not user_id:
        raise AppError("UNAUTHENTICATED", "Your session is invalid or has expired.", 401)
    user = AuthenticatedUser(id=user_id, email=payload.get("email"))
    _verified_tokens[token] = (user, monotonic() + _TOKEN_CACHE_SECONDS)
    return user
