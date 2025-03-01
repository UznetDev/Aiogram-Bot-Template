import logging
import mysql.connector

class Database:

    def __init__(self, host, user, password, database):
        """
        Initialize the Database object with connection parameters.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.reconnect()

    def reconnect(self):
        """
        Reconnect to the MySQL database.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                connection_timeout=30,
                autocommit=True
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            logging.error(f"Database connection error: {err}")
            raise

    def __del__(self):
        """
        Close the database connection when the Database object is deleted.
        """
        try:
            if hasattr(self, 'connection') and self.connection.is_connected():
                self.connection.close()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error in __del__: {err}")
        except Exception as err:
            logging.error(f"General Error in __del__: {err}")

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
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `language_code` VARCHAR(5)
            )
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def create_table_admins(self):
        """
        Create the 'admins' table if it does not already exist.
        """
        try:
            sql = """
                CREATE TABLE IF NOT EXISTS `admins` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `user_id` BIGINT NOT NULL UNIQUE,
                    `initiator_user_id` BIGINT,
                    `updater_user_id` BIGINT,
                    `send_message` TINYINT(1) DEFAULT 0,
                    `statistika` TINYINT(1) DEFAULT 0,
                    `download_statistika` TINYINT(1) DEFAULT 0,
                    `block_user` TINYINT(1) DEFAULT 0,
                    `channel_settings` TINYINT(1) DEFAULT 0,
                    `add_admin` TINYINT(1) DEFAULT 0,
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General error: {err}")

    ## ------------------ Insert data ------------------ ##

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def insert_admin(self, user_id, initiator_user_id):
        """
        Add an admin to the 'admins' table.
        """
        try:
            sql = """
            INSERT INTO admins (user_id, initiator_user_id) VALUES (%s, %s)
            """
            values = (user_id, initiator_user_id)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    ## ------------------ Update ------------------ ##

    def update_settings_key(self, updater_user_id, key, value):
        """
        Update a setting in the 'settings' table.
        """
        try:
            # Removed the extra comma before WHERE clause
            sql = """
            UPDATE settings SET `value` = %s, `updater_user_id` = %s WHERE `key` = %s
            """
            values = (value, updater_user_id, key)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def update_admin_data(self, user_id, column, value, updater_user_id):
        """
        Update an admin's data in the 'admins' table.
        Only allowed columns may be updated.
        """
        allowed_columns = {'send_message', 'statistika', 'download_statistika', 'block_user', 'channel_settings', 'add_admin'}
        if column not in allowed_columns:
            logging.error(f"Invalid column '{column}' specified for update_admin_data")
            return
        try:
            sql = f"UPDATE admins SET {column} = %s, updater_user_id = %s WHERE user_id = %s"
            values = (value, updater_user_id, user_id)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    ## ------------------ Select ------------------ ##

    def select_setting(self, key: str):
        """
        Select a setting from the 'settings' table.
        """
        try:
            sql = "SELECT `value` FROM `settings` WHERE `key` = %s"
            values = (key,)
            self.cursor.execute(sql, values)
            result = self.cursor.fetchone()
            return None if result is None else result['value']
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def delete_user_ban(self, user_id):
        """
        Delete a banned user from the 'users' table.
        """
        try:
            sql = "DELETE FROM users WHERE user_id = %s AND status = 'ban'"
            self.cursor.execute(sql, (user_id,))
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_users_by_id(self, start_id: int, end_id: int) -> list:
        """
        Select users from the 'users' table within a specific ID range.
        """
        try:
            sql = "SELECT * FROM users WHERE id >= %s AND id < %s;"
            values = (start_id, end_id)
            self.cursor.execute(sql, values)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def stat(self):
        """
        Get the total number of users.
        """
        try:
            sql = "SELECT COUNT(*) AS total_users FROM users;"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result['total_users']
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_admin_column(self, user_id, column):
        """
        Select a specific column for an admin from the 'admins' table.
        """
        try:
            sql = f"SELECT {column} AS result FROM admins WHERE user_id = %s"
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_admin(self, user_id):
        """
        Select an admin from the 'admins' table.
        """
        try:
            sql = "SELECT * FROM admins WHERE user_id = %s LIMIT 1"
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_add_admin(self, user_id):
        """
        Select all admins added by a specific admin.
        """
        try:
            sql = "SELECT * FROM admins WHERE initiator_user_id = %s"
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_all_admins(self):
        """
        Select all admins from the 'admins' table.
        """
        try:
            sql = "SELECT * FROM admins"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def stat_admins(self):
        """
        Get the total number of admins.
        """
        try:
            sql = "SELECT COUNT(*) FROM admins"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result[list(result.keys())[0]]
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def delete_admin(self, user_id):
        """
        Delete an admin from the 'admins' table.
        """
        try:
            sql = "DELETE FROM admins WHERE user_id = %s"
            self.cursor.execute(sql, (user_id,))
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_channels(self):
        """
        Select all channels from the 'channels' table.
        """
        try:
            sql = "SELECT * FROM channels"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_channels_initiator_user_id(self, initiator_user_id):
        """
        Select all channels added by a specific admin.
        """
        try:
            sql = "SELECT * FROM channels WHERE initiator_user_id = %s"
            self.cursor.execute(sql, (initiator_user_id,))
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def check_channel(self, channel_id):
        """
        Check if a channel exists in the 'channels' table.
        """
        try:
            sql = "SELECT * FROM channels WHERE channel_id = %s"
            self.cursor.execute(sql, (channel_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_all_channel(self):
        """
        Select all channels from the 'channels' table.
        """
        try:
            sql = "SELECT * FROM channels"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def delete_channel(self, channel_id):
        """
        Delete a channel from the 'channels' table.
        """
        try:
            sql = "DELETE FROM channels WHERE channel_id = %s"
            self.cursor.execute(sql, (channel_id,))
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)
