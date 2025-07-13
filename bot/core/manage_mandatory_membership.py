import json
import logging
import mysql.connector
from redis import Redis
from datetime import datetime


from bot.db.database import Database


class ManageMandatoryMembership:
    _REDIS_HASH = "mandatory_membership"

    def __init__(self, db: Database, redis_client: Redis, root_logger: logging.Logger):
        self.db = db
        self.redis = redis_client
        self.log = root_logger
        self._create_table()

    def channels(self):
        pass

    def update(self, channel_id: int, initiator_user_id: int, is_active: bool):

        current_time = datetime.now()

        redis_key = f"{self.ns}:channels"

        redis_data = self.redis.get(redis_key)
        
        

        cache_data = {
            "channel_id": channel_id,
            "is_active": True,
            "initiator_user_id": initiator_user_id,
            "created_at": current_time.isoformat()
        }
        self.redis.set(redis_key, json.dumps(cache_data))




    def _create_table(self):
        try:
            sql = """
                CREATE TABLE IF NOT EXISTS `channels` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `channel_id` BIGINT,
                    `initiator_user_id` BIGINT,
                    `updater_user_id` BIGINT,
                    `is_active`BOOLEAN DEFAULT TRUE,
                    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                    `deleted_at` TIMESTAMP NULL DEFAULT NULL
                );
            """
            self.db.cursor.execute(sql)
            self.db.connection.commit()
        except mysql.connector.Error as err:
            self.log.error(err)
            self.db()
        except Exception as err:
            self.log.error(err)
