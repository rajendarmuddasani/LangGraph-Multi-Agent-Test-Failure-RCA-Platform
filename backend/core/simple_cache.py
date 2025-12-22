"""
Simple in-memory cache to replace Redis.
"""
from typing import Any, Optional, Dict
import time
import asyncio
from datetime import datetime


class SimpleCache:
    """In-memory cache with TTL support (replaces Redis)."""
    
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """No-op for compatibility with Redis interface."""
        pass
    
    async def close(self):
        """Clear cache on close."""
        self._store.clear()
    
    async def ping(self) -> bool:
        """Always returns True for health checks."""
        return True
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry has expired."""
        if entry.get("expire_at") is None:
            return False
        return time.time() > entry["expire_at"]
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            
            # Check expiration
            if self._is_expired(entry):
                del self._store[key]
                return None
            
            return entry["value"]
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration (seconds)."""
        async with self._lock:
            entry = {
                "value": value,
                "expire_at": time.time() + expire if expire else None,
                "created_at": datetime.utcnow(),
            }
            self._store[key] = entry
            return True
    
    async def delete(self, key: str) -> int:
        """Delete key from cache."""
        async with self._lock:
            if key in self._store:
                del self._store[key]
                return 1
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return False
            
            if self._is_expired(entry):
                del self._store[key]
                return False
            
            return True
    
    async def clear_expired(self):
        """Cleanup expired entries (call periodically)."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._store.items()
                if self._is_expired(entry)
            ]
            for key in expired_keys:
                del self._store[key]
            return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_keys": len(self._store),
            "memory_usage_mb": 0,  # Simplified
            "uptime_seconds": 0,
        }


# Global cache instance
cache = SimpleCache()
