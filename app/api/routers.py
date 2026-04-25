"""
API Routers for the Python Server.
"""

import os
import random
import time
from typing import Any

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, Form, HTTPException, Path, Response
from fastapi.responses import FileResponse, HTMLResponse

from app.services.llm_service import (
    generate_text_with_deepseek,
    generate_text_with_openrouter,
)
from app.services.rate_limiter import rate_limiter_instance

router = APIRouter()
frontend_router = APIRouter()

HTMX_FRONTEND_PATH = "../htmxFrontEnd"


def get_rate_limiter() -> None:
    """Dependency to check rate limit."""
    if rate_limiter_instance.is_exceeded():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    rate_limiter_instance.increment()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": {"$date": {"$numberLong": "2025-01-27T00:00:00.000Z"}},
    }


@router.get("/api/page/home")
async def serve_home_page() -> FileResponse:
    """Serve the home page HTML."""
    return FileResponse(f"{HTMX_FRONTEND_PATH}/html/home.html")


@router.get("/api/page/blog")
async def serve_blog_page() -> FileResponse:
    """Serve the blog page HTML."""
    return FileResponse(f"{HTMX_FRONTEND_PATH}/html/blog.html")


@router.get("/api/page/projects")
async def serve_projects_page() -> FileResponse:
    """Serve the projects page HTML."""
    return FileResponse(f"{HTMX_FRONTEND_PATH}/html/projects.html")


@router.get("/api/page/blog/{post_id}")
async def serve_blog_post(post_id: str = Path(...)) -> FileResponse:
    """Serve a specific blog post."""
    file_path = f"{HTMX_FRONTEND_PATH}/html/blog/{post_id}.html"
    if not os.path.exists(file_path):
        return FileResponse(f"{HTMX_FRONTEND_PATH}/html/blog/blog-not-found.html")
    return FileResponse(file_path)


@router.get("/api/images/{filename}")
async def serve_image(response: Response, filename: str = Path(...)) -> FileResponse:
    """Serve an image with CORS headers."""
    file_path = f"../server/data/images/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"

    return FileResponse(file_path)


@router.get("/api/recursive-window/{remainder}", response_class=HTMLResponse)
async def recursive_window(remainder: int = Path(...)) -> str:
    """Serve a recursive window."""
    if remainder <= 0:
        return ""

    div_id = f"recursive-{remainder}-{int(time.time() * 1000)}"
    hue = (30 + remainder * 20) % 360

    margin_left = random.uniform(1.0, 5.0)
    margin_top = random.uniform(1.0, 5.0)

    html_content = f"""
    <div id="{div_id}"
         hx-get="/api/recursive-window/{remainder - 1}"
         hx-trigger="load"
         style="border: 2px solid hsl({hue}, 70%, 50%);
                position: relative;
                width: 80.0%;
                height: 80.0%;
                min-height: 100px;
                margin-left: {margin_left:.1f}%;
                margin-top: {margin_top:.1f}%;
                padding: 10px;
                box-sizing: border-box;
                background-color: hsla({hue}, 70%, 50%, 0.1);">
    </div>
    <style>
    #{div_id} {{
        animation: fadeIn-{div_id} 1s ease-in-out forwards;
    }}
    @keyframes fadeIn-{div_id} {{
        from {{ opacity: 0; transform: scale(0.9); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}
    </style>
    """
    return html_content


@router.post("/api/generate-css", response_class=HTMLResponse)
async def generate_css(
    prompt: str = Form(...),
    htmlContent: str = Form(""),  # pylint: disable=invalid-name
    _rate_limit: None = Depends(get_rate_limiter),
) -> str:
    """Generate CSS using LLM API."""
    if not prompt:
        raise HTTPException(status_code=400, detail="Input cannot be empty")

    sys_pmt = (
        f"Generate comprehensive CSS styles for an entire website based "
        f"on this description: {prompt}\n"
        "Requirements: Style the entire page, make images fit, "
        "use modern features, make it responsive, write clean CSS.\n"
    )

    if htmlContent:
        sys_pmt += (
            f"\nIMPORTANT: Use the actual HTML structure provided below:\n"
            f"{htmlContent}\n"
        )

    sys_pmt += "\nReturn only the CSS code without any markdown formatting."

    try:
        content = await generate_text_with_deepseek(sys_pmt)
    except Exception:  # pylint: disable=broad-exception-caught
        try:
            content = await generate_text_with_openrouter(sys_pmt)
        except Exception as exc2:  # pylint: disable=broad-exception-caught
            raise HTTPException(
                status_code=500, detail="Failed to generate CSS"
            ) from exc2

    content = content.replace("```css", "").replace("```", "").strip()
    return f"<style id='ai-generated-styles'>{content}</style>"


def inject_hx_get(path: str) -> str:
    """Inject hx-get attribute into the index.html content div."""
    index_path = f"{HTMX_FRONTEND_PATH}/index.html"
    if not os.path.exists(index_path):
        return ""

    with open(index_path, "r", encoding="utf-8") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find(id="content")

    if content_div:
        content_div["hx-get"] = path
        return str(soup)

    return html.replace('hx-get="/api/page/home"', f'hx-get="{path}"', 1)


@frontend_router.get("/home", response_class=HTMLResponse)
async def home_route() -> str:
    """Serve home route."""
    return inject_hx_get("/api/page/home")


@frontend_router.get("/blog", response_class=HTMLResponse)
async def blog_route() -> str:
    """Serve blog route."""
    return inject_hx_get("/api/page/blog")


@frontend_router.get("/projects", response_class=HTMLResponse)
async def projects_route() -> str:
    """Serve projects route."""
    return inject_hx_get("/api/page/projects")


@frontend_router.get("/blog/{post_id}", response_class=HTMLResponse)
async def blog_id_route(post_id: str = Path(...)) -> str:
    """Serve specific blog route."""
    return inject_hx_get(f"/api/page/blog/{post_id}")


@frontend_router.get("/html/footer.html", response_class=HTMLResponse)
async def footer_route() -> FileResponse:
    """Serve footer html."""
    return FileResponse(f"{HTMX_FRONTEND_PATH}/html/footer.html")
