"""
Quick script to create database tables directly
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from database.base import Base
from database.models import (
    RCASession,
    Agent,
    AgentMessage,
    ToolExecution,
    Hypothesis,
    UserFeedback,
    RCAReport,
    STDFDataCache,
    WaferMap,
)
from database.session import engine

async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop existing tables
        await conn.run_sync(Base.metadata.create_all)  # Create fresh tables
    print("✅ All database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
