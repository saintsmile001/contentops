import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.sources import router as sources_router
from app.api.routes.dna import router as dna_router
from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.assets import router as assets_router
from app.api.routes.calendar import router as calendar_router
from app.api.routes.profile import router as profile_router
from app.core.config import get_settings
from app.core.exceptions import AppError, app_error_handler, error_response

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="ContentOps AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(AppError, app_error_handler)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
    return error_response("VALIDATION_ERROR", "Please check the submitted information.", 422, exc.errors())


@app.exception_handler(Exception)
async def unexpected_error_handler(_, exc: Exception) -> JSONResponse:
    logging.getLogger("contentops.errors").exception("Unhandled request error", exc_info=exc)
    return error_response("UNEXPECTED_ERROR", "We couldn't complete that request right now. Please try again.", 500)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, object]:
    return {"data": {"service": "ContentOps AI API"}, "error": None}


app.include_router(health_router, prefix="/api")
app.include_router(sources_router, prefix="/api")
app.include_router(dna_router, prefix="/api")
app.include_router(campaigns_router, prefix="/api")
app.include_router(assets_router, prefix="/api")
app.include_router(calendar_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
