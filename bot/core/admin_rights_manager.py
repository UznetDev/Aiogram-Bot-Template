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


    def __call__(self, user_id: int, feature: str, return_intiator: bool = False) -> Optional[bool]:
        
        if user_id == ADMIN: return True
        if not self[user_id][0]: return None

        key = f"{self.ns}:{user_id}:features:feature:{feature}:is_active"

        if (cached := self.redis.get(key)) is not None:
            if return_intiator:
                initiator_key = f"{self.ns}:{user_id}:features:feature:{feature}:initiator_user_id"
                initiator_user_id = self.redis.get(initiator_key)
                return cached == "1", int(initiator_user_id) if initiator_user_id else None
            return cached == "1"

        try:
            sql = f"""
                SELECT 
                    `value`
                    {", `initiator_user_id`" if return_intiator else ""}
                FROM `admin_rights` AS ar
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
                if return_intiator:
                    initiator_user_id = row.get("initiator_user_id")
                    initiator_key = f"{self.ns}:{user_id}:features:feature:{feature}:initiator_user_id"
                    self.redis.set(initiator_key, initiator_user_id)
                    return value, int(initiator_user_id)
                return value
        
            if return_intiator:
                return None, None
            return None
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (get) xatosi: {err}")
            self.db.reconnect()
            return None

    def __getitem__(self, user_id: int) -> (bool | int):
        if user_id == ADMIN: return True, None, "super_admin"

        is_active = f"{self.ns}:{user_id}:is_active"
        cached = self.redis.get(is_active)
        initiator_user_id = self.redis.get(f"{self.ns}:{user_id}:initiator_user_id") 
        role = self.redis.get(f"{self.ns}:{user_id}:role")

        if cached is not None:
            return cached == "1", int(initiator_user_id), role
        try:
            sql = """
                SELECT
                    `is_active`,
                    `initiator_user_id`,
                    `role`
                FROM `admins
                WHERE `user_id` = %s
                  AND  `is_active` = TRUE
                LIMIT 1;
            """
            self.db.cursor.execute(sql, (user_id,))
            row = self.db.cursor.fetchone()
            if not row:
                return False, None, None
            is_admin = row["is_active"]

            self.redis.set(is_active, "1" if is_admin else "0")
            self.redis.set(f"{self.ns}:{user_id}:initiator_user_id", row["initiator_user_id"])
            self.redis.set(f"{self.ns}:{user_id}:role", row["role"])
            return is_admin, row["initiator_user_id"], row["role"]
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (is_admin) xatosi: {err}")
            self.db.reconnect()
            return False

    def update(self, user_id: int, feature: str, value: bool, initiator_user_id: int) -> None:
        try:
            is_admin = self[user_id]
            check = self(user_id, feature, return_intiator=True)
            if initiator_user_id == check[1] or is_admin[1] == initiator_user_id or initiator_user_id == ADMIN:
                if is_admin[0] is False:
                    self.log.warning(f"User {user_id} is not an admin, cannot update feature {feature}.")
                    return
                elif check[0] == value:
                    self.log.info(f"Feature {feature} for user {user_id} is already set to {value}.")
                    return
                elif check[0]:
                    self.db.cursor.execute(
                        "UPDATE `admin_rights` SET `value` = %s, `updater_user_id` = %s WHERE `admin_id` = (SELECT id FROM admins WHERE user_id = %s) AND `name` = %s;",
                        (value, initiator_user_id, user_id, feature)
                    )
                else:
                    self.db.cursor.execute(
                        "INSERT INTO `admin_rights` (`admin_id`, `name`, `value`, `initiator_user_id`) VALUES ((SELECT id FROM admins WHERE user_id = %s), %s, %s, %s);",
                        (user_id, feature, value, initiator_user_id)
                    )
                self.redis.set(f"{self.ns}:{user_id}:features:feature:{feature}:is_active", "1" if value else "0")
                self.redis.set(f"{self.ns}:{user_id}:features:feature:{feature}:initiator_user_id", initiator_user_id)
                self.db.connection.commit()
            else:
                self.log.warning(f"User {initiator_user_id} is not authorized to update feature {feature} for user {user_id}.")
                return
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (update) xatosi: {err}")
            self.db.reconnect()
            return

        # Redis keshini yangilash
        key = self._redis_key(user_id, feature)
        self.redis.set(key, "1" if value else "0")

    def add(self, user_id: int, initiator_user_id: int, role: str = 'admin') -> None:
        try:
            if self[user_id][0]:
                return

            self.db.cursor.execute(
                "INSERT INTO `admins` (`user_id`, `initiator_user_id`, `role`) VALUES (%s, %s, %s);",
                (user_id, initiator_user_id, role),
            )
            self.db.connection.commit()
            self.redis.set(f"{self.ns}:{user_id}:is_active", "1")
            self.redis.set(f"{self.ns}:{user_id}:initiator_user_id", initiator_user_id)
            self.redis.set(f"{self.ns}:{user_id}:role", role)
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (add) xatosi: {err}")
            self.db.reconnect()

    def remove(self, user_id: int, initiator_user_id: int) -> None:
        try:
            check = self[user_id]
            if not check[0]:
                return
            elif check[1] == initiator_user_id:
                sql = """
                    UPDATE `admins`
                    SET `is_active` = FALSE, `deleted_at` = CURRENT_TIMESTAMP, `updater_user_id` = %s
                    WHERE `user_id` = %s;
                """
                self.db.cursor.execute(sql, (initiator_user_id, user_id))
                self.db.connection.commit()
                self.redis.set(f"{self.ns}:{user_id}:is_active", "0")
                self.redis.set(f"{self.ns}:{user_id}:initiator_user_id", initiator_user_id)
                self.redis.set(f"{self.ns}:{user_id}:role", None)
        
        except mysql.connector.Error as err:
            self.log.error(f"MySQL (remove) xatosi: {err}")
            self.db.reconnect()

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
    
