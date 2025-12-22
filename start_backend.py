#!/usr/bin/env python
"""
Start the FastAPI backend with environment variables loaded.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Verify OpenAI key is loaded
if not os.getenv("OPENAI_API_KEY"):
    print("❌ ERROR: OPENAI_API_KEY not found in .env file!")
    sys.exit(1)

print(f"✅ Loaded environment variables from {env_path}")
print(f"✅ OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:20]}...")
print(f"✅ DATABASE_URL: {os.getenv('DATABASE_URL')}")
print("\nStarting FastAPI backend...\n")

# Now import and run
import uvicorn
sys.path.insert(0, str(Path(__file__).parent / "backend"))

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
