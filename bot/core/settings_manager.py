import logging
from typing import Optional, Any
import mysql.connector
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
        self._ensure_table()

    def __call__(self, key: str) -> Optional[str]:
        return self.get(key)
        
    def get(self, key: str) -> Optional[str]:
        """Kesh → DB tartibida o‘qish."""
        try:
            cached = self.redis.hget(self._REDIS_HASH, key)
            if cached is not None:
                return cached

            sql = "SELECT `value` FROM `settings` WHERE `key` = %s"
            self.db.cursor.execute(sql, (key,))
            row = self.db.cursor.fetchone()
            if row is None:
                return None

            self.redis.hset(self._REDIS_HASH, key, row["value"])
            return row["value"]

        except (RedisError, mysql.connector.Error, Exception) as exc:
            self.log.error(f"SettingsManager.get('{key}') → {exc}")
            if isinstance(exc, mysql.connector.Error):
                self.db.reconnect()
            return None

    def upsert(self, key: str, value: Any, user_id: int = -1) -> None:
        try:
            sql = """
            INSERT INTO `settings`
                (`key`, `value`, `initiator_user_id`, `updater_user_id`)
            VALUES
                (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                `value`            = VALUES(`value`),
                `updater_user_id`  = VALUES(`updater_user_id`),
                `updated_at`       = CURRENT_TIMESTAMP
            """
            vals = (key, str(value), user_id, user_id)
            self.db.cursor.execute(sql, vals)
            self.db.connection.commit()

            self.redis.hset(self._REDIS_HASH, key, str(value))
            self.log.info(f"Setting '{key}' → {value}")

        except RedisError as exc:
            self.log.error(f"Redis error upserting '{key}': {exc}")

        except mysql.connector.Error as err:
            self.log.error(f"MySQL error upserting '{key}': {err}")
            self.db.reconnect()
            raise

        except Exception as exc:
            self.log.error(f"Unknown error upserting '{key}': {exc}")
            raise

    def _ensure_table(self) -> None:
        try:
            self.db.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `settings` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `key` VARCHAR(255) NOT NULL UNIQUE,
                    `value` VARCHAR(255) NOT NULL,
                    `initiator_user_id` BIGINT,
                    `updater_user_id` BIGINT,
                    `updated_at` TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `deleted_at` TIMESTAMP NULL
                )
                """
            )
            self.db.connection.commit()
        except mysql.connector.Error as err:
            self.log.error(f"Error creating settings table: {err}")
            self.db.reconnect()
