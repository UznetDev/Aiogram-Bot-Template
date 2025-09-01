import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis
import mysql.connector

from bot.data.config import ADMIN
from bot.db.database import Database


class ManageMandatoryMembership:
    """
    Manage mandatory membership channels for a Telegram bot.

    - Data model fields:
        id, channel_id, initiator_user_id, updater_user_id,
        is_active, created_at, updated_at, deleted_at

    - Redis key:
        "mandatory_membership:{channel_id}" -> JSON-serialized channel row

    - Rules:
        * Reads prefer Redis; if missing/stale, fall back to MySQL and refresh Redis.
        * If channel doesn't exist on update(), it is created with initiator_user_id = updater_user_id.
        * Only the original initiator or ADMIN can update an existing channel.
        * channels(initiator_user_id) returns active channel IDs:
            - If initiator_user_id is None or ADMIN -> all active channels.
            - Else -> active channels added by that initiator_user_id.
    """

    TABLE = "mandatory_memberships"
    REDIS_PREFIX = "mandatory_membership"

    def __init__(
        self,
        db: Database,
        redis_client: redis.Redis,
        root_logger: Optional[logging.Logger] = None,
    ):
        self.db = db
        self.r = redis_client
        self.log = root_logger or logging.getLogger(__name__)
        self._create_table()

    # ---------- Public API ----------

    def channels(self, initiator_user_id: Optional[int]) -> List[int]:
        """
        Return list of ACTIVE channel_ids filtered by initiator_user_id.
        - None or ADMIN -> all active channels
        - Otherwise -> only active channels added by that initiator_user_id
        """
        # Try to build from Redis (best-effort)
        redis_ids = self._channels_from_redis(initiator_user_id)

        # Always verify/correct with DB to guarantee completeness/consistency
        if initiator_user_id is None or initiator_user_id == ADMIN:
            sql = f"""
                SELECT channel_id
                FROM {self.TABLE}
                WHERE is_active = 1 AND deleted_at IS NULL
            """
            params = ()
        else:
            sql = f"""
                SELECT channel_id
                FROM {self.TABLE}
                WHERE is_active = 1
                  AND initiator_user_id = %s
                  AND deleted_at IS NULL
            """
            params = (initiator_user_id,)

        try:
            self.db.cursor.execute(sql, params)
            rows = self.db.cursor.fetchall() or []
        except mysql.connector.Error as err:
            self.log.error(f"[channels] MySQL error: {err}")
            # If DB fails, fall back to Redis result (possibly partial)
            return sorted(redis_ids)

        db_ids = [int(r["channel_id"]) for r in rows]

        # Write-through: ensure all DB rows are cached in Redis
        if db_ids:
            self._refresh_cache_for_ids(db_ids)

        # DB is the source of truth; return DB-derived list
        return sorted(db_ids)

    def update(self, channel_id: int, is_active: bool, updater_user_id: int) -> Dict[str, Any]:
        """
        Create or update a channel record.
        - If record doesn't exist -> insert with initiator_user_id = updater_user_id
        - If exists -> only initiator_user_id or ADMIN may update
        - Write-first to MySQL, then update Redis
        Returns the up-to-date row as a dict.
        """
        if channel_id is None:
            raise ValueError("channel_id is required")
        if updater_user_id is None:
            raise ValueError("updater_user_id is required")

        is_active_int = 1 if bool(is_active) else 0

        # 1) Try Redis, then MySQL
        row = self._get_from_cache(channel_id)
        if row is None:
            row = self._get_from_db_by_channel_id(channel_id)

        # 2) Insert or Update with permission checks
        if row is None:
            # Insert new
            new_row_id = self._insert_row(
                channel_id=channel_id,
                initiator_user_id=updater_user_id,
                updater_user_id=updater_user_id,
                is_active=is_active_int,
            )
            row = self._get_from_db_by_id(new_row_id)
            if row is None:
                raise RuntimeError("Insert succeeded but failed to re-fetch the row")
        else:
            # Permission check
            initiator_id = int(row["initiator_user_id"])
            if updater_user_id != initiator_id and updater_user_id != ADMIN:
                raise PermissionError(
                    "Only the initiator of this channel or the ADMIN can update it."
                )
            # Update existing
            self._update_row(
                row_id=int(row["id"]),
                is_active=is_active_int,
                updater_user_id=updater_user_id,
            )
            row = self._get_from_db_by_channel_id(channel_id)
            if row is None:
                raise RuntimeError("Update succeeded but failed to re-fetch the row")

        # 3) Sync Redis
        self._set_cache_row(row)
        return row

    # ---------- Private: Schema ----------

    def _create_table(self) -> None:
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{self.TABLE}` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `channel_id` BIGINT NOT NULL UNIQUE,
            `initiator_user_id` BIGINT NOT NULL,
            `updater_user_id` BIGINT DEFAULT NULL,
            `is_active` TINYINT(1) NOT NULL DEFAULT 1,
            `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            `deleted_at` DATETIME DEFAULT NULL,
            INDEX idx_active (is_active),
            INDEX idx_initiator (initiator_user_id),
            INDEX idx_deleted (deleted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        try:
            self.db.cursor.execute(sql)
            # autocommit is True in your Database class, no need to commit explicitly
            self.log.debug(f"Ensured table `{self.TABLE}` exists.")
        except mysql.connector.Error as err:
            self.log.error(f"[create_table] MySQL error: {err}")
            raise

    # ---------- Private: Redis helpers ----------

    def _key(self, channel_id: int) -> str:
        return f"{self.REDIS_PREFIX}:{channel_id}"

    def _get_from_cache(self, channel_id: int) -> Optional[Dict[str, Any]]:
        try:
            raw = self.r.get(self._key(channel_id))
            if not raw:
                return None
            data = json.loads(raw)
            # Ensure keys we rely on exist
            if "channel_id" not in data or "id" not in data:
                return None
            return data
        except Exception as e:
            self.log.warning(f"[cache:get] Redis error for {channel_id}: {e}")
            return None

    def _set_cache_row(self, row: Dict[str, Any]) -> None:
        try:
            # Make datetime fields JSON-serializable
            serializable = row.copy()
            for k in ("created_at", "updated_at", "deleted_at"):
                if serializable.get(k) is not None and not isinstance(serializable[k], str):
                    # MySQL connector may return datetime objects; store as ISO8601 strings
                    serializable[k] = serializable[k].isoformat(sep=" ", timespec="seconds")
            self.r.set(self._key(int(row["channel_id"])), json.dumps(serializable))
        except Exception as e:
            self.log.warning(f"[cache:set] Redis error for {row.get('channel_id')}: {e}")

    def _channels_from_redis(self, initiator_user_id: Optional[int]) -> List[int]:
        """
        Best-effort scan of Redis to collect active channel_ids (may be partial).
        """
        try:
            pattern = f"{self.REDIS_PREFIX}:*"
            channel_ids: List[int] = []
            for key in self.r.scan_iter(match=pattern, count=1000):
                try:
                    raw = self.r.get(key)
                    if not raw:
                        continue
                    data = json.loads(raw)
                    if int(data.get("is_active", 0)) != 1:
                        continue
                    if initiator_user_id is None or initiator_user_id == ADMIN:
                        channel_ids.append(int(data["channel_id"]))
                    else:
                        if int(data.get("initiator_user_id", -1)) == int(initiator_user_id):
                            channel_ids.append(int(data["channel_id"]))
                except Exception:
                    continue
            return sorted(set(channel_ids))
        except Exception as e:
            self.log.debug(f"[channels_from_redis] scan failed: {e}")
            return []

    def _refresh_cache_for_ids(self, channel_ids: List[int]) -> None:
        """
        Ensure Redis has up-to-date rows for the provided channel_ids (from DB).
        """
        if not channel_ids:
            return
        fmt = ",".join(["%s"] * len(channel_ids))
        sql = f"""
            SELECT *
            FROM {self.TABLE}
            WHERE channel_id IN ({fmt}) AND deleted_at IS NULL
        """
        try:
            self.db.cursor.execute(sql, tuple(channel_ids))
            rows = self.db.cursor.fetchall() or []
            for row in rows:
                self._set_cache_row(row)
        except mysql.connector.Error as err:
            self.log.debug(f"[refresh_cache] MySQL error: {err}")

    # ---------- Private: DB ops ----------

    def _get_from_db_by_channel_id(self, channel_id: int) -> Optional[Dict[str, Any]]:
        sql = f"""
            SELECT *
            FROM {self.TABLE}
            WHERE channel_id = %s AND deleted_at IS NULL
            LIMIT 1
        """
        try:
            self.db.cursor.execute(sql, (channel_id,))
            return self.db.cursor.fetchone()
        except mysql.connector.Error as err:
            self.log.error(f"[db:get_by_channel] MySQL error: {err}")
            return None

    def _get_from_db_by_id(self, row_id: int) -> Optional[Dict[str, Any]]:
        sql = f"SELECT * FROM {self.TABLE} WHERE id = %s LIMIT 1"
        try:
            self.db.cursor.execute(sql, (row_id,))
            return self.db.cursor.fetchone()
        except mysql.connector.Error as err:
            self.log.error(f"[db:get_by_id] MySQL error: {err}")
            return None

    def _insert_row(
        self,
        channel_id: int,
        initiator_user_id: int,
        updater_user_id: int,
        is_active: int,
    ) -> int:
        sql = f"""
            INSERT INTO {self.TABLE}
                (channel_id, initiator_user_id, updater_user_id, is_active, created_at, updated_at, deleted_at)
            VALUES
                (%s, %s, %s, %s, %s, %s, NULL)
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.db.cursor.execute(
                sql,
                (channel_id, initiator_user_id, updater_user_id, is_active, now, now),
            )
            # autocommit enabled
            last_id = self.db.cursor.lastrowid
            self.log.info(f"[insert] Added channel {channel_id} by {initiator_user_id} (id={last_id})")
            return int(last_id)
        except mysql.connector.errors.IntegrityError as err:
            # Handle unique violation on channel_id -> convert to update
            self.log.warning(f"[insert] IntegrityError (exists?) for channel {channel_id}: {err}")
            existing = self._get_from_db_by_channel_id(channel_id)
            if existing:
                return int(existing["id"])
            raise
        except mysql.connector.Error as err:
            self.log.error(f"[insert] MySQL error: {err}")
            raise

    def _update_row(self, row_id: int, is_active: int, updater_user_id: int) -> None:
        sql = f"""
            UPDATE {self.TABLE}
            SET is_active = %s,
                updater_user_id = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND deleted_at IS NULL
        """
        try:
            self.db.cursor.execute(sql, (is_active, updater_user_id, row_id))
            self.log.info(f"[update] Row id={row_id} set is_active={is_active} by {updater_user_id}")
        except mysql.connector.Error as err:
            self.log.error(f"[update] MySQL error: {err}")
            raise

    # ---------- (Optional) Utilities ----------

    def get(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a single channel row (active or inactive, but not soft-deleted).
        Redis first; if missing then DB, and refresh cache.
        """
        row = self._get_from_cache(channel_id)
        if row is None:
            row = self._get_from_db_by_channel_id(channel_id)
            if row:
                self._set_cache_row(row)
        return row

    def soft_delete(self, channel_id: int, deleter_user_id: int) -> bool:
        """
        Soft delete (set deleted_at) — optional helper if you need it later.
        Only initiator or ADMIN may delete.
        """
        row = self._get_from_cache(channel_id) or self._get_from_db_by_channel_id(channel_id)
        if not row:
            return False
        initiator_id = int(row["initiator_user_id"])
        if deleter_user_id != initiator_id and deleter_user_id != ADMIN:
            raise PermissionError("Only the initiator or ADMIN can delete this channel.")

        sql = f"""
            UPDATE {self.TABLE}
            SET deleted_at = CURRENT_TIMESTAMP,
                updater_user_id = %s
            WHERE id = %s AND deleted_at IS NULL
        """
        try:
            self.db.cursor.execute(sql, (deleter_user_id, int(row["id"])))
            # Remove from cache so it won't be returned accidentally
            try:
                self.r.delete(self._key(channel_id))
            except Exception:
                pass
            return True
        except mysql.connector.Error as err:
            self.log.error(f"[soft_delete] MySQL error: {err}")
            return False
