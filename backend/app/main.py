"""Main FastAPI application entry point for LinkIntel AI."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import settings
from .api.routes import router
from .utils.logging import logger, log_event


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application instance."""
    app = FastAPI(
        title="LinkIntel AI",
        description=(
            "AI-powered website intelligence platform that transforms public business websites "
            "into structured competitive, search, SEO, service, and audience intelligence."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS strictly from environment settings
    origins = settings.parsed_frontend_origins
    allow_all = "*" in origins or (settings.app_env == "development" and not origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else origins,
        allow_credentials=False if allow_all else True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Register API routes
    app.include_router(router)

    # Global validation error handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        first_error = exc.errors()[0] if exc.errors() else {}
        msg = first_error.get("msg", "Invalid request body.")
        loc = " -> ".join([str(l) for l in first_error.get("loc", [])])
        detail = f"Validation failed at '{loc}': {msg}"
        log_event("request_validation_failed", path=request.url.path, detail=detail)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": detail, "errors": jsonable_encoder(exc.errors())},
        )

    # General unhandled exception handler
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred while processing the request."},
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.app_port, reload=True)
