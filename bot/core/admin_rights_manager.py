# bot/core/admin_rights_manager.py
import logging
from typing import Optional

import mysql.connector
from redis import Redis

from bot.db.database import Database
from bot.data.config import ADMIN


class AdminsManager:
    def __init__(
        self,
        db: Database,
        redis_client: Redis,
        root_logger: logging.Logger,
        redis_namespace: str = "admin_setting",
    ) -> None:
        self.db = db
        self.redis = redis_client
        self.ns = redis_namespace
        self.log = root_logger.getChild(self.__class__.__name__)
        self.create_table_admins()
        self.create_table_admin_rights()

    def __call__(self, user_id: int, feature: str) -> Optional[bool]:
        return self.get(user_id, feature) or user_id == ADMIN

    def get(self, user_id: int, feature: str = None) -> Optional[bool]:
        
        if user_id == ADMIN: return True
        if feature is None: return self.is_admin(user_id)

        key = self._redis_key(user_id, feature)

        if (cached := self.redis.get(key)) is not None:
            return cached == "1"

        try:
            sql = """
                SELECT `value`
                FROM   `admin_rights` AS ar
                INNER JOIN `admins` AS a
                    ON ar.admin_id=a.id
                WHERE  a.user_id = %s
                    AND `name` = %s
                    AND ar.`is_active` = TRUE
                LIMIT  1
            """
            self.db.cursor.execute(sql, (user_id, feature))
            row = self.db.cursor.fetchone()
            if row:
                value = bool(row["value"])
                self.redis.set(key, "1" if value else "0")
                return value
            return None
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (get) xatosi: {err}")
            self.db.reconnect()
            return None

    def is_admin(self, user_id: int) -> bool:
        if user_id == ADMIN: return True

        key = f"{self.ns}:{user_id}:__is_admin__"
        cached = self.redis.get(key)
        if cached is not None:
            return cached == "1"
        try:
            sql = """
                SELECT 1
                FROM   admins
                WHERE  user_id = %s
                  AND  is_active = TRUE
                LIMIT 1;
            """
            self.db.cursor.execute(sql, (user_id,))
            row = self.db.cursor.fetchone()
            is_admin = bool(row)
            self.redis.set(key, "1" if is_admin else "0")
            return is_admin
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (is_admin) xatosi: {err}")
            self.db.reconnect()
            return False

    def update(self, user_id: int, feature: str, value: bool, is_active: bool = True) -> None:
        try:
            sql = """
                INSERT INTO admin_rights (admin_id, name, value, is_active)
                VALUES (
                    (SELECT id FROM admins WHERE user_id = %s),
                    %s,  -- feature
                    %s,  -- value
                    %s   -- is_active
                )
                ON DUPLICATE KEY UPDATE
                    value      = VALUES(value),
                    is_active  = VALUES(is_active),
                    updated_at = CURRENT_TIMESTAMP;
            """
            self.db.cursor.execute(sql, (user_id, feature, int(value), is_active))
            self.db.connection.commit()
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (update) xatosi: {err}")
            self.db.reconnect()
            return

        # Redis keshini yangilash
        key = self._redis_key(user_id, feature)
        self.redis.set(key, "1" if value else "0")

    def add(self, user_id: int) -> None:
        try:
            self.db.cursor.execute(
                "INSERT INTO `admins` (`user_id`) VALUES (%s);",
                (user_id,),
            )
            self.db.connection.commit()
            key = f"{self.ns}:{user_id}:__is_admin__"
            self.redis.set(key, "1")
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (add) xatosi: {err}")
            self.db.reconnect()

    def _redis_key(self, admin_id: int, feature: str) -> str:
        return f"{self.ns}:{admin_id}:{feature}"
    
    def create_table_admins(self):
        try:
            sql = """
                CREATE TABLE IF NOT EXISTS `admins` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `user_id` BIGINT NOT NULL UNIQUE,
                    `initiator_user_id` BIGINT,
                    `updater_user_id` BIGINT,
                    `role` ENUM('admin', 'moderator') DEFAULT 'admin',
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

    def create_table_admin_rights(self):
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS `admin_rights` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `admin_id` INT NOT NULL,
                `name` VARCHAR(255) NOT NULL,
                `value` BOOLEAN NOT NULL,
                `is_active` BOOLEAN DEFAULT TRUE,
                `description` TEXT,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `deleted_at` TIMESTAMP NULL,
                UNIQUE KEY `uq_admin_feature` (`admin_id`,`name`),
                CONSTRAINT `fk_rights_admin`
                    FOREIGN KEY (`admin_id`) REFERENCES `admins`(`id`)
                    ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            self.db.cursor.execute(sql)
            self.db.connection.commit()
        except mysql.connector.Error as err:
            self.log.error(err)
            self.db.reconnect()
        except Exception as err:
            self.log.error(err)
            self.db.reconnect()
    
