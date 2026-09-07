from fastapi import APIRouter, Depends

from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.db.database import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(settings: Settings = Depends(get_app_settings)) -> dict[str, object]:
    database = await check_database_connection(settings)
    return {
        "data": {
            "status": "ok",
            "environment": settings.app_env,
            "database": "not_configured" if database is None else ("connected" if database else "unavailable"),
        },
        "error": None,
    }

