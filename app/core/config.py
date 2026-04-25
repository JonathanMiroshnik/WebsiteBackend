"""
Configuration module for the Python Server.

This module loads environment variables and provides them
to the rest of the application.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration settings."""

    PORT: int = int(os.getenv("PORT", "5000"))
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    LLM_SERVICE_ACTIVATED: bool = (
        os.getenv("LLM_SERVICE_ACTIVATED", "false").lower() == "true"
    )
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    OPENROUTER_API: str = os.getenv("OPENROUTER_API", "")
    OPENROUTER_MODEL: str = os.getenv(
        "OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324:free"
    )
    CLIENT_URL: str = os.getenv("CLIENT_URL", "http://localhost:5000")


config = Config()
