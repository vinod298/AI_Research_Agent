import time
from typing import Any, Optional
import redis.asyncio as aioredis
from config.settings import settings
from config.logger import logger


class RedisCacheManager:
    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._memory_store: dict = {}
        self._memory_expirations: dict = {}

    async def initialize(self) -> None:
        """Connect to Redis if available, else setup fallback."""
        try:
            url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            if settings.REDIS_PASSWORD:
                url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            
            client = aioredis.from_url(url, encoding="utf-8", decode_responses=True, socket_connect_timeout=2)
            await client.ping()
            self._redis = client
            logger.info("Connected to Redis cache server.")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}). Fallback to in-memory cache mode.")
            self._redis = None

    async def get(self, key: str) -> Optional[str]:
        if self._redis:
            try:
                return await self._redis.get(key)
            except Exception:
                pass
        
        # Fallback in-memory
        if key in self._memory_store:
            exp = self._memory_expirations.get(key)
            if exp and time.time() > exp:
                del self._memory_store[key]
                del self._memory_expirations[key]
                return None
            return self._memory_store.get(key)
        return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        if self._redis:
            try:
                if ttl:
                    await self._redis.setex(key, ttl, value)
                else:
                    await self._redis.set(key, value)
                return True
            except Exception:
                pass

        # Fallback in-memory
        self._memory_store[key] = value
        if ttl:
            self._memory_expirations[key] = time.time() + ttl
        return True

    async def incr(self, key: str, ttl: Optional[int] = None) -> int:
        """Increment key value for rate-limiting."""
        if self._redis:
            try:
                val = await self._redis.incr(key)
                if val == 1 and ttl:
                    await self._redis.expire(key, ttl)
                return val
            except Exception:
                pass

        # Fallback in-memory
        current_str = await self.get(key)
        val = int(current_str) + 1 if current_str else 1
        await self.set(key, str(val), ttl=ttl)
        return val

    async def delete(self, key: str) -> bool:
        if self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                pass
        if key in self._memory_store:
            del self._memory_store[key]
        if key in self._memory_expirations:
            del self._memory_expirations[key]
        return True

    async def close(self):
        if self._redis:
            await self._redis.close()


redis_manager = RedisCacheManager()
