import json
import logging
from datetime import datetime
from typing import List, Optional, Dict

import mysql.connector
from redis import Redis

from bot.data.config import ADMIN
from bot.db.database import Database


class ManageMandatoryMembership:
    """Manage list of mandatory channels with Redis and MySQL."""

    _REDIS_HASH = "mandatory_membership"

    def __init__(self, db: Database, redis_client: Redis, root_logger: logging.Logger) -> None:
        self.db = db
        self.redis = redis_client
        self.log = root_logger
        self._ensure_table()

    # ------------------------------------------------------------------
    def channels(self) -> List[int]:
        """Return list of active channel IDs."""
        try:
            redis_key = f"{self._REDIS_HASH}:all"
            cached = self.redis.get(redis_key)
            if cached:
                return json.loads(cached)

            self.db.cursor.execute(
                "SELECT channel_id FROM channels WHERE is_active = TRUE AND deleted_at IS NULL"
            )
            rows = self.db.cursor.fetchall() or []
            channel_ids = [row["channel_id"] for row in rows]
            self.redis.set(redis_key, json.dumps(channel_ids))
            return channel_ids
        except mysql.connector.Error as err:
            self.log.error(f"MySQL error in channels(): {err}")
            self.db.reconnect()
            return []
        except Exception as err:
            self.log.error(f"Error in channels(): {err}")
            return []

    # ------------------------------------------------------------------
    def update(self, channel_id: int, is_active: bool, updater_user_id: int) -> None:
        """Insert or update a channel record.

        The channel is created if it does not exist. Existing records can only be
        updated by their creator or the super admin defined in :data:`ADMIN`.
        All changes are synchronized between MySQL and Redis.
        """
        try:
            now = datetime.now()
            redis_key = f"{self._REDIS_HASH}:{channel_id}"
            cached = self.redis.get(redis_key)
            channel: Optional[Dict] = json.loads(cached) if cached else None

            if channel is None:
                self.db.cursor.execute(
                    "SELECT * FROM channels WHERE channel_id=%s AND deleted_at IS NULL",
                    (channel_id,),
                )
                channel = self.db.cursor.fetchone()
                if channel:
                    self.redis.set(redis_key, json.dumps(channel))

            if channel:
                initiator_id = channel.get("initiator_user_id") if isinstance(channel, dict) else channel["initiator_user_id"]
                if updater_user_id != ADMIN and updater_user_id != initiator_id:
                    self.log.warning(
                        "User %s is not allowed to update channel %s", updater_user_id, channel_id
                    )
                    return

                sql = (
                    "UPDATE channels SET is_active=%s, updater_user_id=%s, updated_at=%s WHERE channel_id=%s"
                )
                self.db.cursor.execute(sql, (is_active, updater_user_id, now, channel_id))
                self.db.connection.commit()

                channel = dict(channel)
                channel.update(
                    {
                        "is_active": is_active,
                        "updater_user_id": updater_user_id,
                        "updated_at": now.isoformat(),
                    }
                )
            else:
                sql = (
                    "INSERT INTO channels (channel_id, initiator_user_id, updater_user_id, "
                    "is_active, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)"
                )
                self.db.cursor.execute(
                    sql,
                    (channel_id, updater_user_id, updater_user_id, is_active, now, now),
                )
                self.db.connection.commit()
                channel = {
                    "channel_id": channel_id,
                    "initiator_user_id": updater_user_id,
                    "updater_user_id": updater_user_id,
                    "is_active": is_active,
                    "created_at": now.isoformat(),
                    "updated_at": now.isoformat(),
                    "deleted_at": None,
                }

            self.redis.set(redis_key, json.dumps(channel))
            self.redis.delete(f"{self._REDIS_HASH}:all")
        except mysql.connector.Error as err:
            self.log.error(f"MySQL error in update(): {err}")
            self.db.reconnect()
        except Exception as err:
            self.log.error(f"Error in update(): {err}")

    # ------------------------------------------------------------------
    def _ensure_table(self) -> None:
        """Ensure the ``channels`` table exists."""
        try:
            sql = """
                CREATE TABLE IF NOT EXISTS `channels` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `channel_id` BIGINT,
                    `initiator_user_id` BIGINT,
                    `updater_user_id` BIGINT,
                    `is_active` BOOLEAN DEFAULT TRUE,
                    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                    `deleted_at` TIMESTAMP NULL DEFAULT NULL
                );
            """
            self.db.cursor.execute(sql)
            self.db.connection.commit()
        except mysql.connector.Error as err:
            self.log.error(err)
            self.db.reconnect()
        except Exception as err:
            self.log.error(err)

