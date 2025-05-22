import logging
from typing import Optional
from bot.db.database import Database
from redis import Redis, RedisError
import mysql.connector

class FeatureManager:
    _REDIS_HASH = "features"

    def __init__(self, db: Database, redis_client: Redis, root_logger: logging.Logger):
        self.db = db
        self.redis = redis_client
        self.log = root_logger
        self._create_table_features()

    def __call__(self, name: str) -> bool:
        return self.feature(name)

    def feature(self, name: str) -> bool:
        """Kesh → DB → (birinchi marta bo‘lsa) foydalanuvchidan so‘rash."""
        try:
            cached = self._get_from_redis(name)
            if cached is not None:
                return cached

            db_val = self._select_enabled(name)
            if db_val is not None:
                self.redis.hset(self._REDIS_HASH, name, int(db_val))
                return bool(db_val)

            enabled = self._ask_user(name)
            self.upsert_feature(name, enabled)
            return enabled

        except (RedisError, Exception) as exc:
            self.log.error(f"Error in feature('{name}'): {exc}")
            return False

    def upsert_feature(self, name: str, enabled: bool) -> None:
        try:
            sql = """
                INSERT INTO features        (name, enabled)
                VALUES                      (%s,   %s)
                ON DUPLICATE KEY UPDATE
                    enabled    = VALUES(enabled),
                    updated_at = CURRENT_TIMESTAMP,
                    deleted_at = NULL
            """
            self.db.cursor.execute(sql, (name, int(enabled)))
            self.db.connection.commit()


            self.redis.hset(self._REDIS_HASH, name, int(enabled))
            self.log.info("Feature '%s' upserted → %s", name, enabled)

        except mysql.connector.Error as err:
            self.log.error(err)
            self.db.reconnect()
        except Exception as err:
            self.log.error(err)
            raise

    def _get_from_redis(self, name: str) -> Optional[bool]:
        val = self.redis.hget(self._REDIS_HASH, name)
        return bool(int(val)) if val is not None else None

    def _ask_user(self, name: str) -> bool:
        return input(f"Feature '{name}' not found, enable it? (y/n): ").strip().lower() == "y"

    def _select_enabled(self, name: str) -> Optional[bool]:
        try:
            self.db.cursor.execute("SELECT `enabled` FROM `features` WHERE `name` = %s LIMIT 1", (name,))
            row = self.db.cursor.fetchone()
            return None if row is None else bool(row["enabled"])
        except mysql.connector.Error as err:
            self.log.error(err)
            self.db.reconnect()
        except Exception as err:
            self.log.error(err)


    def _create_table_features(self):
        try:
            self.db.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS features (
                    id         INT AUTO_INCREMENT PRIMARY KEY,
                    name       VARCHAR(255) NOT NULL UNIQUE,
                    enabled    TINYINT(1)  NOT NULL DEFAULT 0,
                    updated_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP            DEFAULT NULL,
                    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self.db.connection.commit()
        except mysql.connector.Error as err:
            self.log.error(err)
            self.db.reconnect()
        except Exception as err:
            self.log.error(err)
