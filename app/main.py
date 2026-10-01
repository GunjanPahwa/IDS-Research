"""FastAPI Main Application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import health, model, predict
from app.core.errors import (
    NIDSException,
    generic_exception_handler,
    http_exception_handler,
    nids_exception_handler,
    validation_exception_handler,
)
from app.core.logging import logger, setup_logging
from app.core.middleware import RequestIDMiddleware
from app.services.inference import inference_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager handling application startup and shutdown events."""
    setup_logging()
    logger.info("Starting NIDS Backend API...")
    # Preload models once at startup
    inference_service.load_all_models()
    yield
    logger.info("Shutting down NIDS Backend API...")


app = FastAPI(
    title="Network Intrusion Detection System (NIDS) API",
    description="Inference API serving Unified Single-Stage Multi-Class prediction models across 6 network datasets.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Request ID & Latency Tracking Middleware
app.add_middleware(RequestIDMiddleware)

# Centralized Exception Handlers
app.add_exception_handler(NIDSException, nids_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include v1 API Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(model.router, prefix="/api/v1")
app.include_router(predict.router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root_redirect():
    """Root status summary."""
    return {
        "message": "Network Intrusion Detection System (NIDS) API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "version": "1.0.0",
    }
