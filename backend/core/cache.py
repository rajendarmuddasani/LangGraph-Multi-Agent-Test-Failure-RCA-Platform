"""
Cache client - now using simple in-memory cache instead of Redis.
For production, switch to Redis by changing the import below.
"""
from core.simple_cache import cache

# Expose cache instance for backwards compatibility
__all__ = ["cache"]
