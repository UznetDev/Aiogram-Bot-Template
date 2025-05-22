import logging
from typing import Optional
from bot.db.database import Database
from redis import Redis, RedisError
import mysql.connector

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
        self.create_table_features()

    def feature(self, name: str) -> bool:
        try:
            cached = self._get_from_redis(name)
            if cached is not None:
                return cached

            db_value = self.select_feature(name)
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
            if rows == 0:
                self.insert_feature(name=name, enabled=enabled)

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
        self.insert_feature(name=name, enabled=enabled)
        self.redis.hset(self._REDIS_HASH, name, int(enabled))

    def create_table_features(self):
        try:
            sql = """
                CREATE TABLE IF NOT EXISTS `features` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `name` VARCHAR(255) NOT NULL UNIQUE,
                    `enabled` TINYINT(1) DEFAULT 0,
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `deleted_at` TIMESTAMP NULL DEFAULT NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            self.db.cursor.execute(sql)
            self.db.connection.commit()
        except mysql.connector.Error as err:
            self.log.error(err)
            self.db.reconnect()
        except Exception as err:
            self.log.error(err)

    def insert_feature(self, name: str, enabled: bool):
        try:
            sql = "INSERT INTO `features` (`name`, `enabled`) VALUES (%s, %s)"
            values = (name, int(enabled))
            self.db.cursor.execute(sql, values)
            self.db.connection.commit()
        except mysql.connector.Error as err:
            self.log.error(err)
            self.db.reconnect()
        except Exception as err:
            self.db.root_logger.error(err)

    def select_feature(self, name: str):
        try:
            sql = "SELECT * FROM `features` WHERE `name` = %s"
            values = (name,)
            self.db.cursor.execute(sql, values)
            result = self.db.cursor.fetchone()
            return None if result is None else result['enabled']
        except mysql.connector.Error as err:
            self.log.error(err)
            self.db.reconnect()
        except Exception as err:
            self.log.error(err)
