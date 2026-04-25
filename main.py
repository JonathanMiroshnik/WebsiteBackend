"""
Main application entry point for the Python Server.
"""

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routers import frontend_router
from app.api.routers import router as api_router
from app.core.config import config

app = FastAPI(title="Python Server", version="1.0.0")

# Configure CORS
origins = [
    "https://www.sensorcensor.xyz",
    "https://real.sensorcensor.xyz",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "PUT", "PATCH", "POST", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "hx-current-url",
        "hx-request",
        "hx-target",
        "hx-trigger",
    ],
    expose_headers=["Content-Type", "Content-Length"],
)

# Include routers
app.include_router(api_router)
app.include_router(frontend_router)

# Mount static files
HTMX_FRONTEND_PATH = "../htmxFrontEnd"
if os.path.exists(f"{HTMX_FRONTEND_PATH}/css"):
    app.mount("/css", StaticFiles(directory=f"{HTMX_FRONTEND_PATH}/css"), name="css")
if os.path.exists(f"{HTMX_FRONTEND_PATH}/js"):
    app.mount("/js", StaticFiles(directory=f"{HTMX_FRONTEND_PATH}/js"), name="js")
if os.path.exists(f"{HTMX_FRONTEND_PATH}/assets"):
    app.mount(
        "/assets", StaticFiles(directory=f"{HTMX_FRONTEND_PATH}/assets"), name="assets"
    )


@app.exception_handler(404)
async def catch_all(_request: Request, _exc: Exception) -> FileResponse:
    """Catch-all route for SPA routing - always serve index.html."""
    return FileResponse(f"{HTMX_FRONTEND_PATH}/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
