"""
LLM Service handles interactions with language models.
"""

from typing import Any, Dict

import httpx

from app.core.config import config


async def generate_text_with_deepseek(prompt: str) -> str:
    """Generate text using DeepSeek LLM service."""
    if not config.DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY key not found in environment")

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": config.LLM_MAX_TOKENS,
        "temperature": 1.5,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            "https://api.deepseek.com/chat/completions", json=payload, headers=headers
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("choices"):
            raise ValueError("DeepSeek API returned no choices")

        return str(data["choices"][0]["message"]["content"])


async def generate_text_with_openrouter(prompt: str) -> str:
    """Generate text using OpenRouter LLM service."""
    if not config.OPENROUTER_API:
        raise ValueError("OPENROUTER_API key not found in environment")

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {config.OPENROUTER_API}",
        "HTTP-Referer": config.CLIENT_URL,
        "X-Title": "PythonServer",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "model": config.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": config.LLM_MAX_TOKENS,
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("choices"):
            raise ValueError("OpenRouter API returned no choices")

        return str(data["choices"][0]["message"]["content"])
