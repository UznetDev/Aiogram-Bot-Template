import logging
import mysql.connector
from aiogram import Bot


class Database:
    def __init__(self, host, user, password, database, root_logger: logging.Logger):
        """
        Initialize the Database object with connection parameters.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.root_logger = root_logger
        self.reconnect()
        self.create_table_users()
        self.create_table_channel()
        self.create_table_settings()
        self.create_table_texts()
        self.create_table_translations()

    def reconnect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                connection_timeout=30,
                autocommit=True
            )
            self.cursor = self.connection.cursor(dictionary=True, buffered=True)
        except mysql.connector.Error as err:
            self.root_logger.error(f"Database connection error: {err}")
            raise

    def __del__(self):
        """
        Close the database connection when the Database object is deleted.
        """
        try:
            if hasattr(self, 'connection') and self.connection.is_connected():
                self.connection.close()
        except mysql.connector.Error as err:
            self.root_logger.error(f"MySQL Error in __del__: {err}")
        except Exception as err:
            self.root_logger.error(f"General Error in __del__: {err}")

    ## --------------------- Create table ------------------##

    def create_table_users(self):
        """
        Create the 'users' table if it does not already exist.
        """
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS `users` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `user_id` BIGINT NOT NULL UNIQUE,
                `status` ENUM('remove', 'active', 'blocked', 'ban', 'unban', 'sleep') DEFAULT 'active',
                `initiator_user_id` BIGINT,
                `updater_user_id` BIGINT,
                `comment` TEXT,
                `ban_time` TIMESTAMP NULL DEFAULT NULL,
                `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                `deleted_at` TIMESTAMP NULL DEFAULT NULL,
                `language_code` VARCHAR(5)
            )
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def create_table_channel(self):
        """
        Create the 'channels' table if it does not already exist.
        """
        try:
            sql = """
                CREATE TABLE IF NOT EXISTS `channels` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `channel_id` BIGINT,
                    `initiator_user_id` BIGINT,
                    `updater_user_id` BIGINT,
                    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                    `deleted_at` TIMESTAMP NULL DEFAULT NULL
                );
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)
            
    def create_table_settings(self):
        """
        Create the 'settings' table if it does not already exist.
        """
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS `settings` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `updater_user_id` BIGINT,
                `initiator_user_id` BIGINT,
                `key` VARCHAR(255) NOT NULL,
                `value` VARCHAR(255) NOT NULL,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `deleted_at` TIMESTAMP NULL
            )
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)
    
    def create_table_texts(self):
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS texts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hash_value BIGINT UNSIGNED,
                raw_text TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP NULL DEFAULT NULL,
                INDEX(hash_value)
            )
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def create_table_translations(self):
        try:
            sql = """
                CREATE TABLE IF NOT EXISTS `translations` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `text_id` INT NOT NULL,
                    `dest_lang` CHAR(5) NOT NULL,
                    `translated_content` TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL DEFAULT NULL,
                    FOREIGN KEY (text_id) REFERENCES texts(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)


    ## ---------------- Scheduler ---------------------
    def ban_user_for_one_hour(self, user_id, comment=None):
        """
        Ban a user for one hour and create an event to unban them.
        """
        try:
            sql_update = """
                UPDATE users 
                SET status = 'ban', ban_time = NOW(), initiator_user_id = 1, updater_user_id = 1, comment = %s
                WHERE user_id = %s
            """
            self.cursor.execute(sql_update, (comment, user_id))
            self.connection.commit()

            event_name = f"unban_user_{user_id}"
            # Wrap the event name in backticks in case of naming issues
            sql_event = f"""
                CREATE EVENT IF NOT EXISTS `{event_name}`
                ON SCHEDULE AT DATE_ADD(NOW(), INTERVAL 1 HOUR)
                DO
                    UPDATE users 
                    SET status = 'active', ban_time = NULL, updater_user_id = 1
                    WHERE user_id = %s;
            """
            self.cursor.execute(sql_event, (user_id,))
            _ = self.cursor.fetchall()  # Natijani o‘qish orqali tozalaymiz
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(f"MySQL error: {err}")
            self.reconnect()
        except Exception as err:
            self.root_logger.error(f"General error: {err}")

    ## ------------------ Insert data ------------------ ##

    def insert_texts(self, hash_value: str, raw_text: str):
        """
        Insert a new text into the 'texts' table.
        """
        try:
            sql = "INSERT INTO `texts` (`hash_value`, `raw_text`) VALUES (%s, %s)"
            values = (hash_value, raw_text)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def insert_translations(self, text_id: int, dest_lang: str, translated_content: str):
        try:
            sql = "INSERT INTO `translations` (`text_id`, `dest_lang`, `translated_content`) VALUES (%s, %s, %s)"
            values = (text_id, dest_lang, translated_content)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def insert_settings(self, initiator_user_id, key, value):
        """
        Add a setting to the 'settings' table.
        """
        try:
            sql = "INSERT INTO `settings` (`updater_user_id`, `initiator_user_id`, `key`, `value`) VALUES (%s, %s, %s, %s)"
            values = (initiator_user_id, initiator_user_id, key, value)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def insert_user(self, user_id, language_code):
        """
        Add a user to the 'users' table.
        """
        try:
            sql = """
            INSERT INTO users (user_id, language_code) VALUES (%s, %s)
            """
            values = (user_id, language_code)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def insert_channel(self, channel_id, initiator_user_id):
        """
        Add a channel to the 'channels' table.
        """
        try:
            sql = """
            INSERT INTO channels (channel_id, initiator_user_id) VALUES (%s, %s)
            """
            values = (channel_id, initiator_user_id)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    ## ------------------ Update ------------------ ##
    def update_feature(self, name: str, enabled: bool):
        """
        Update a feature in the 'features' table.
        """
        try:
            sql = "UPDATE `features` SET `enabled` = %s WHERE `name` = %s"
            values = (int(enabled), name)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def update_settings_key(self, updater_user_id, key, value):
        try:
            sql = """
            UPDATE settings SET `value` = %s, `updater_user_id` = %s WHERE `key` = %s
            """
            values = (value, updater_user_id, key)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def update_user_status(self, user_id, status, updater_user_id):
        """
        Update a user's status in the 'users' table.
        """
        try:
            sql = "UPDATE users SET status = %s, updater_user_id = %s WHERE user_id = %s"
            values = (status, updater_user_id, user_id)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    ## ------------------ Select ------------------ ##

    def select_texts(self, hash_value: str):
        try:
            sql = "SELECT * FROM `texts` WHERE `hash_value` = %s LIMIT 1"
            values = (hash_value,)
            self.cursor.execute(sql, values)
            result = self.cursor.fetchone()
            return None if result is None else result['id']
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def select_translations(self, text_id: int, dest_lang: str):
        try:
            sql = "SELECT * FROM `translations` WHERE `text_id` = %s AND `dest_lang` = %s LIMIT 1"
            values = (text_id, dest_lang)
            self.cursor.execute(sql, values)
            result = self.cursor.fetchone()
            return None if result is None else result['translated_content']
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def select_setting(self, key: str):
        try:
            sql = "SELECT `value` FROM `settings` WHERE `key` = %s"
            values = (key,)
            self.cursor.execute(sql, values)
            result = self.cursor.fetchone()
            return None if result is None else result['value']
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def select_all_users_ban(self):
        """
        Select all banned users from the 'users' table.
        """
        try:
            sql = "SELECT * FROM users WHERE status = 'ban'"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def stat_ban(self):
        """
        Get the total number of banned users.
        """
        try:
            sql = "SELECT COUNT(*) AS user_count FROM users WHERE status = 'ban';"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result['user_count']
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def check_user_ban(self, user_id):
        """
        Check if a user is banned.
        """
        try:
            sql = "SELECT * FROM users WHERE status = 'ban' AND user_id = %s"
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def delete_user_ban(self, user_id):
        """
        Delete a banned user from the 'users' table.
        """
        try:
            sql = "DELETE FROM users WHERE user_id = %s AND status = 'ban'"
            self.cursor.execute(sql, (user_id,))
            self.connection.commit()
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def select_all_users(self):
        """
        Select all users from the 'users' table.
        """
        try:
            sql = "SELECT * FROM users"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

        """
        Get the total number of users.
        """
        try:
            sql = "SELECT COUNT(*) AS total_users FROM users;"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result['total_users']
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)

    def check_user(self, user_id):
        """
        Check if a user exists in the 'users' table.
        """
        try:
            sql = "SELECT * FROM users WHERE user_id = %s"
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            self.root_logger.error(err)
            self.reconnect()
        except Exception as err:
            self.root_logger.error(err)




class MySQLHandler(logging.Handler):
    def __init__(self, bot: Bot, connection: mysql.connector.MySQLConnection):
        super().__init__()
        try:
            self.bot = bot
            self.connection = connection
            self.cursor = self.connection.cursor()
            self.create_table()
        except Exception as err:
            print(err)

    def create_table(self):
        try:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS `log_history` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `pathname` VARCHAR(255),
                `filename` VARCHAR(255),
                `funcname` VARCHAR(255),
                `lineno` INT,
                `logger_name` VARCHAR(255),
                `level` VARCHAR(50),
                `message` TEXT,
                `create_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_table_query)
            self.connection.commit()
        except  Exception as err:
            print(err)
            
        except Exception as err:
            print(err)


    def emit(self, record):
        try:
            sql = """
            INSERT INTO `log_history` (`pathname`, `filename`, `funcname`, `lineno`, `logger_name`, `level`, `message`)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                record.pathname,
                record.filename,
                record.funcName,
                record.lineno,
                record.name,
                record.levelname,
                record.getMessage()
            )
            self.cursor.execute(sql, values)
            self.connection.commit()
        except Exception as err:
            print(err)


    def close(self):
        self.cursor.close()
        self.connection.close()
        super().close()