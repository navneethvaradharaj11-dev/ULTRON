import logging
import json
from typing import Optional, Any, Dict
from app.config.settings import settings

logger = logging.getLogger("ULTRON.Redis")


class RedisClient:
    """Production Redis Client abstraction for locks, queues, rate limiting, and caching.
    Falls back gracefully to in-memory store if Redis is unavailable or unconfigured.
    """

    def __init__(self):
        self._memory_store: Dict[str, Any] = {}
        self._memory_queues: Dict[str, list] = {}
        self._is_redis_available = False
        self._redis_conn = None
        self._init_redis()

    def _init_redis(self):
        try:
            import redis
            self._redis_conn = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD or None,
                db=settings.REDIS_DB,
                socket_timeout=2.0,
                decode_responses=True
            )
            self._redis_conn.ping()
            self._is_redis_available = True
            logger.info("Redis connection established successfully at %s:%s", settings.REDIS_HOST, settings.REDIS_PORT)
        except Exception as e:
            self._is_redis_available = False
            logger.info("Redis not available (%s); operating with in-memory fallback store.", e)

    @property
    def is_available(self) -> bool:
        return self._is_redis_available

    def set_key(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """Set a key in Redis or memory store."""
        val_str = json.dumps(value) if not isinstance(value, str) else value
        if self._is_redis_available and self._redis_conn:
            try:
                self._redis_conn.set(key, val_str, ex=expire_seconds)
                return True
            except Exception as e:
                logger.warning("Redis set_key failed: %s; falling back to memory store", e)
        self._memory_store[key] = val_str
        return True

    def get_key(self, key: str) -> Optional[str]:
        """Get a key from Redis or memory store."""
        if self._is_redis_available and self._redis_conn:
            try:
                val = self._redis_conn.get(key)
                if val is not None:
                    return val
            except Exception as e:
                logger.warning("Redis get_key failed: %s; using memory store", e)
        return self._memory_store.get(key)

    def delete_key(self, key: str) -> bool:
        """Delete a key from Redis or memory store."""
        if self._is_redis_available and self._redis_conn:
            try:
                self._redis_conn.delete(key)
            except Exception:
                pass
        self._memory_store.pop(key, None)
        return True

    def acquire_lock(self, lock_name: str, timeout_seconds: int = 10) -> bool:
        """Acquire a distributed lock."""
        lock_key = f"lock:{lock_name}"
        if self._is_redis_available and self._redis_conn:
            try:
                return bool(self._redis_conn.set(lock_key, "1", nx=True, ex=timeout_seconds))
            except Exception:
                pass
        if lock_key not in self._memory_store:
            self._memory_store[lock_key] = "1"
            return True
        return False

    def release_lock(self, lock_name: str) -> None:
        """Release a distributed lock."""
        lock_key = f"lock:{lock_name}"
        self.delete_key(lock_key)

    def enqueue_job(self, queue_name: str, job_data: Dict[str, Any]) -> bool:
        """Enqueue a background job payload."""
        payload = json.dumps(job_data)
        queue_key = f"queue:{queue_name}"
        if self._is_redis_available and self._redis_conn:
            try:
                self._redis_conn.rpush(queue_key, payload)
                return True
            except Exception as e:
                logger.warning("Redis rpush failed: %s; queuing in memory", e)
        if queue_key not in self._memory_queues:
            self._memory_queues[queue_key] = []
        self._memory_queues[queue_key].append(payload)
        return True

    def dequeue_job(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Dequeue a background job payload."""
        queue_key = f"queue:{queue_name}"
        payload = None
        if self._is_redis_available and self._redis_conn:
            try:
                payload = self._redis_conn.lpop(queue_key)
            except Exception:
                pass
        if not payload and queue_key in self._memory_queues and self._memory_queues[queue_key]:
            payload = self._memory_queues[queue_key].pop(0)

        if payload:
            try:
                return json.loads(payload)
            except Exception:
                return {"raw": payload}
        return None


redis_client = RedisClient()
