import logging
from typing import Optional, Any

from redis import Redis, RedisError
from bot.db.database import Database


class SettingsManager:
    _REDIS_HASH = "settings"

    def __init__(
        self,
        db: Database,
        redis_client: Redis,
        root_logger: logging.Logger,
    ):
        self.db: Database = db
        self.redis: Redis = redis_client
        self.log: logging.Logger = root_logger

    def get(self, key: str) -> Optional[str]:
        try:
            cached = self._get_from_redis(key)
            if cached is not None:
                return cached

            db_val = self.db.select_setting(key)
            if db_val is None:
                return None

            self.redis.hset(self._REDIS_HASH, key, db_val)
            return db_val

        except (RedisError, Exception) as exc:
            self.log.error(f"Error in SettingsManager.get('{key}'): {exc}")
            return None

    def update(self, key: str, value: Any, updater_user_id: int = -1) -> None:
        try:
            check = self.db.select_setting(key)
            if check is None:
                self.db.insert_settings(
                    initiator_user_id=updater_user_id,
                    key=key,
                    value=str(value),
                )
            else:
                self.db.update_settings_key(
                    updater_user_id=updater_user_id,
                    key=key,
                    value=str(value),
                )
            self.redis.hset(self._REDIS_HASH, key, str(value))
            self.log.info(f"Setting '{key}' updated → {value}")

        except (RedisError, Exception) as exc:
            self.log.error(f"Error in SettingsManager.update('{key}', '{value}'): {exc}")
            raise

    def _get_from_redis(self, key: str) -> Optional[str]:
        val = self.redis.hget(self._REDIS_HASH, key)
        return val if val is not None else None
