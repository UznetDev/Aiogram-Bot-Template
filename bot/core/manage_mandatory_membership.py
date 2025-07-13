import json
import datetime
import logging
import mysql.connector
import redis
from bot.data.config import ADMIN
from bot.db.database import Database


class ManageMandatoryMembership:
    """
    Manages mandatory membership channels for a Telegram bot, synchronizing Redis cache and MySQL storage.
    """
    def __init__(self, db: Database, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        self._create_table()

    def _create_table(self):
        """
        Ensures the `mandatory_membership` table exists in MySQL.
        """
        sql = """
        CREATE TABLE IF NOT EXISTS mandatory_membership (
            id INT AUTO_INCREMENT PRIMARY KEY,
            channel_id BIGINT NOT NULL UNIQUE,
            initiator_user_id BIGINT NOT NULL,
            updater_user_id BIGINT,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            deleted_at DATETIME NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self.db.cursor.execute(sql)

    def channels(self) -> list[int]:
        """
        Returns a list of all active channel IDs.
        Attempts to read from Redis first; if cache is empty, falls back to MySQL and repopulates cache.
        """
        pattern = "mandatory_membership:*"
        try:
            keys = self.redis.keys(pattern)
        except Exception as e:
            self.logger.error(f"Redis error on keys(): {e}")
            keys = []

        active_channels = []
        for key in keys:
            try:
                raw = self.redis.get(key)
                if not raw:
                    continue
                record = json.loads(raw)
                if record.get("is_active"):
                    active_channels.append(int(record["channel_id"]))
            except Exception:
                continue

        if active_channels:
            return active_channels

        # Cache miss: load from DB
        sql = (
            "SELECT id, channel_id, initiator_user_id, updater_user_id, is_active, created_at, updated_at, deleted_at "
            "FROM mandatory_membership WHERE is_active = 1 AND deleted_at IS NULL"
        )
        self.db.cursor.execute(sql)
        rows = self.db.cursor.fetchall()

        for row in rows:
            key = f"mandatory_membership:{row['channel_id']}"
            record = {
                "id": row["id"],
                "channel_id": row["channel_id"],
                "initiator_user_id": row["initiator_user_id"],
                "updater_user_id": row["updater_user_id"],
                "is_active": bool(row["is_active"]),
                "created_at": row["created_at"].isoformat(),
                "updated_at": row["updated_at"].isoformat(),
                "deleted_at": row["deleted_at"].isoformat() if row["deleted_at"] else None
            }
            try:
                self.redis.set(key, json.dumps(record))
            except Exception as e:
                self.logger.error(f"Redis error on set(): {e}")
            active_channels.append(int(row["channel_id"]))

        return active_channels

    def update(self, channel_id: int, is_active: bool, updater_user_id: int) -> dict:
        """
        Adds a new channel or updates the active status of an existing one.

        - If the channel does not exist, it is inserted (initiator_user_id = updater_user_id).
        - If it exists, only the original initiator or super admin may update it.
        - Synchronizes changes to both MySQL and Redis.

        Returns the record dict after update.
        """
        now = datetime.datetime.utcnow()
        # Check for existing record
        sql_select = (
            "SELECT * FROM mandatory_membership WHERE channel_id = %s AND deleted_at IS NULL"
        )
        self.db.cursor.execute(sql_select, (channel_id,))
        row = self.db.cursor.fetchone()

        deleted_at = None
        if row is None:
            # Insert new record
            sql_insert = (
                "INSERT INTO mandatory_membership "
                "(channel_id, initiator_user_id, updater_user_id, is_active, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            self.db.cursor.execute(sql_insert, (
                channel_id,
                updater_user_id,
                updater_user_id,
                int(is_active),
                now,
                now
            ))
            record_id = self.db.cursor.lastrowid
            initiator_id = updater_user_id
            created_at = now
        else:
            # Permission check
            initiator_id = row["initiator_user_id"]
            created_at = row["created_at"]
            if updater_user_id not in (initiator_id, ADMIN):
                raise PermissionError("Only the initiator or super admin can update this channel")
            # Handle deactivation
            if not is_active:
                deleted_at = now
            sql_update = (
                "UPDATE mandatory_membership SET is_active = %s, updater_user_id = %s, updated_at = %s, deleted_at = %s "
                "WHERE channel_id = %s"
            )
            self.db.cursor.execute(sql_update, (
                int(is_active),
                updater_user_id,
                now,
                deleted_at,
                channel_id
            ))
            record_id = row["id"]

        # Build cache record
        cache_key = f"mandatory_membership:{channel_id}"
        cache_record = {
            "id": record_id,
            "channel_id": channel_id,
            "initiator_user_id": initiator_id,
            "updater_user_id": updater_user_id,
            "is_active": is_active,
            "created_at": created_at.isoformat(),
            "updated_at": now.isoformat(),
            "deleted_at": deleted_at.isoformat() if deleted_at else None
        }
        try:
            self.redis.set(cache_key, json.dumps(cache_record))
        except Exception as e:
            self.logger.error(f"Redis error on set(): {e}")

        return cache_record
