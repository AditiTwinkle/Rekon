"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time

from rekon.core.config import settings
from rekon.core.exceptions import RekonException
from rekon.utils.logging import configure_logging, get_logger
from rekon.api.routes import regulations

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI-powered audit and compliance platform",
)

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request/response logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=process_time,
    )
    
    return response


# Exception handlers
@app.exception_handler(RekonException)
async def rekon_exception_handler(request: Request, exc: RekonException):
    """Handle Rekon exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
            }
        },
    )


from rekon.api.routes import (
    regulations,
    checklists,
    compliance,
    gaps,
    remediation,
    evidence,
    reports,
    dashboard,
)

# Include routers
app.include_router(regulations.router)
app.include_router(checklists.router)
app.include_router(compliance.router)
app.include_router(gaps.router)
app.include_router(remediation.router)
app.include_router(evidence.router)
app.include_router(reports.router)
app.include_router(dashboard.router)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


@app.get("/")
def root() -> dict:
    """Root endpoint.

    Returns:
        API information
    """
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": "AI-powered audit and compliance platform",
    }


@app.on_event("startup")
async def startup_event() -> None:
    """Handle startup event."""
    logger.info("Rekon API starting up", version=settings.api_version)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Handle shutdown event."""
    logger.info("Rekon API shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "rekon.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=True,
    )
