"""
Conftest for LangGraph Multi-Agent RCA Platform.
Stubs heavy optional packages (structlog, langchain*, langgraph) before
any backend import, so tests run without the full production stack.
"""
import sys
import os
from unittest.mock import MagicMock

# ── 1. Stub unavailable / heavyweight packages ──────────────────────────────
for mod_name in [
    "structlog",
    "langchain_openai",
    "langchain",
    "langchain.agents",
    "langchain.tools",
    "langgraph",
    "langgraph.graph",
    "alembic",
]:
    sys.modules.setdefault(mod_name, MagicMock())

# ── 2. Required env vars — config.py validates these at import time ─────────
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake-key-for-ci-testing")
os.environ.setdefault("JWT_SECRET_KEY", "fake-jwt-secret-key-for-test-env!!!!!!")
os.environ.setdefault("DATABASE_URL",
    "postgresql+asyncpg://rca_user:password@localhost:5432/rca_platform")
os.environ.setdefault("ENVIRONMENT", "development")

# ── 3. Patch sys.path so `from core.config import ...` resolves ─────────────
BACKEND = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)
