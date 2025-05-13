import logging
from typing import Optional
from db.database import Database
from redis import Redis, RedisError


class FeatureManager:
    _REDIS_HASH = "features"

    def __init__(
        self,
        db: Database,
        redis_client: Redis,
        root_logger: logging.Logger,
    ):
        self.db = db
        self.redis = redis_client
        self.log = root_logger

    def feature(self, name: str) -> bool:
        try:
            cached = self._get_from_redis(name)
            if cached is not None:
                return cached

            db_value = self.db.select_feature(name)
            if db_value is None:
                enabled = self._ask_user(name)
                self._persist(name, enabled)
                return enabled

            self.redis.hset(self._REDIS_HASH, name, int(db_value))
            return bool(db_value)

        except (RedisError, Exception) as exc:
            self.log.error(f"Error in feature('{name}'): {exc}")
            return False

    def update_feature(self, name: str, enabled: bool) -> None:
        try:
            rows = self.db.update_feature(name=name, enabled=enabled)
            if rows == 0:                           # feature yo‘q edi
                self.db.insert_feature(name=name, enabled=enabled)

            self.redis.hset(self._REDIS_HASH, name, int(enabled))

            self.log.info(f"Feature '{name}' updated → {enabled}")

        except (RedisError, Exception) as exc:
            self.log.error(f"Error in update_feature('{name}'): {exc}")
            raise

    def _get_from_redis(self, name: str) -> Optional[bool]:
        val = self.redis.hget(self._REDIS_HASH, name)
        return bool(int(val)) if val is not None else None

    def _ask_user(self, name: str) -> bool:
        access = input(
            f"Feature '{name}' not found, do you want to enable it? (y/n): "
        )
        return access.strip().lower() == "y"

    def _persist(self, name: str, enabled: bool) -> None:
        self.db.insert_feature(name=name, enabled=enabled)
        self.redis.hset(self._REDIS_HASH, name, int(enabled))
