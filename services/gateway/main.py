"""
BATMAN API Gateway
==================
FastAPI application serving as the single entry point for all BATMAN services.
Handles: Authentication (JWT/Keycloak), routing, rate limiting, request logging.
Port: 8080
"""
from contextlib import asynccontextmanager
from typing import Annotated

import structlog
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from .config import Settings
from .middleware.auth import verify_jwt_token, TokenData
from .routers import missions, coa, simulation, threats, gis, audit, health

logger = structlog.get_logger(__name__)
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("BATMAN Gateway starting", version="2.0.0")
    yield
    logger.info("BATMAN Gateway shutting down")


app = FastAPI(
    title="BATMAN — Battlefield Analytics & Tactical Mission Assistance Network",
    description=(
        "Command Decision Support System API. "
        "All AI recommendations require explicit commander authorization. "
        "Classification: UNCLASSIFIED — Academic/Research Purpose Only."
    ),
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── MIDDLEWARE ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.TRUSTED_HOSTS,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured request logging for all HTTP traffic."""
    log = logger.bind(
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown",
    )
    log.info("request_received")
    response = await call_next(request)
    log.info("request_completed", status_code=response.status_code)
    return response


# ── PROMETHEUS METRICS ────────────────────────────────────────────────────────

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# ── ROUTERS ───────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(health.router,      prefix=API_PREFIX, tags=["Health"])
app.include_router(missions.router,    prefix=API_PREFIX, tags=["Missions"])
app.include_router(coa.router,         prefix=API_PREFIX, tags=["Courses of Action"])
app.include_router(simulation.router,  prefix=API_PREFIX, tags=["War Gaming"])
app.include_router(threats.router,     prefix=API_PREFIX, tags=["Threat Assessment"])
app.include_router(gis.router,         prefix=API_PREFIX, tags=["GIS / Terrain"])
app.include_router(audit.router,       prefix=API_PREFIX, tags=["Audit"])


# ── EXCEPTION HANDLERS ────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("http_exception", status=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "status_code": 500},
    )
