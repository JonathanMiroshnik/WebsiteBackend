# AGENTS.md — Developer & AI Agent Guide

## Project Overview

This is a **FastAPI-based Python backend** that serves an HTMX frontend. It provides:
- Static file serving for an HTMX frontend (HTML, CSS, JS, assets)
- LLM-powered CSS generation via DeepSeek and OpenRouter APIs
- Blog/project page routing
- Image serving with CORS headers
- Rate limiting

## Secrets & Security

### No Hardcoded Secrets

All sensitive values are loaded from **environment variables** via `python-dotenv` (see `app/core/config.py`). The following keys are expected:

| Variable | Purpose |
|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek LLM API key |
| `OPENROUTER_API` | OpenRouter LLM API key |
| `PORT` | Server port (default: 5000) |
| `LLM_SERVICE_ACTIVATED` | Toggle LLM features |
| `LLM_MAX_TOKENS` | Max tokens for LLM responses |
| `OPENROUTER_MODEL` | Model identifier for OpenRouter |
| `CLIENT_URL` | CORS origin URL |

### Before You Commit / Push

**Do NOT commit `.env` files or any file containing real API keys, tokens, or passwords.**

The project has **pre-commit hooks** installed that automatically scan for secrets before every commit. Here's what you need to know:

1. **Pre-commit hooks are installed** — They run automatically on `git commit`. If a secret is detected, the commit will be **blocked**.

2. **To manually scan for secrets** at any time:
   ```bash
   detect-secrets scan --all-files
   ```

3. **To scan a specific file**:
   ```bash
   detect-secrets scan path/to/file.py
   ```

4. **If you need to update the secrets baseline** (e.g., after adding a new file that contains non-secret high-entropy strings):
   ```bash
   detect-secrets scan --all-files > .secrets.baseline
   ```

5. **To bypass pre-commit hooks in an emergency** (not recommended):
   ```bash
   git commit --no-verify
   ```

### What's Protected by `.gitignore`

The following are excluded from git tracking:
- `.env`, `.env.local`, `.env.production`, `.env.development`
- `__pycache__/` and compiled Python files
- IDE/editor config files (`.vscode/`, `.idea/`)
- Virtual environments (`venv/`, `.venv/`, `env/`)
- Log files

### Setting Up a New Developer

1. Copy `.env.example` to `.env` and fill in real values:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Key Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI app entry point, CORS config, static file mounting |
| `app/core/config.py` | Environment variable loading via `python-dotenv` |
| `app/api/routers.py` | All API routes (health, pages, blog, CSS generation, images) |
| `app/services/llm_service.py` | DeepSeek and OpenRouter API clients |
| `app/services/rate_limiter.py` | Simple thread-safe rate limiter |
| `.pre-commit-config.yaml` | Pre-commit hook configuration (secret detection, linting) |
| `.secrets.baseline` | Baseline for `detect-secrets` — commit this file |
| `.env.example` | Template for required environment variables |
| `.gitignore` | Files excluded from version control |

## Architecture Notes

- **Rate limiting**: 1000 requests per hour per instance (configurable in `rate_limiter.py`)
- **LLM fallback**: CSS generation first tries DeepSeek, falls back to OpenRouter on failure
- **SPA routing**: All unmatched routes serve `index.html` for client-side routing
- **HTMX frontend**: Expected at `../htmxFrontEnd` relative to the backend directory
