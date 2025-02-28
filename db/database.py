import logging
import mysql.connector


class Database:

    def __init__(self, host, user, password, database):
        """
        Initialize the Database object with connection parameters.

        Parameters:
        host (str): The hostname of the MySQL server.
        user (str): The username to connect to the MySQL server.
        password (str): The password to connect to the MySQL server.
        database (str): The name of the database to connect to.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.reconnect()


    def reconnect(self):
        """
        Reconnect to the MySQL database.

        This method initializes or re-initializes the database connection and cursor
        objects. It is generally called:
          - Right after the object is created (inside __init__).
          - After a failed connection or if a connection error occurs.
        
        If the connection is successful, `self.connection` and `self.cursor` are 
        reset. If it fails, an error is logged and re-raised.

        Returns:
            None

        Raises:
            mysql.connector.Error: 
                If connecting to the database fails due to invalid credentials, 
                unreachable host, etc.

        Example:
            >>> db = Database("root", "secret", "my_database")
            >>> # If for some reason the connection is lost, you can manually reconnect:
            >>> db.reconnect()
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
            self.connection.close()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")


    ## --------------------- Create table ------------------##


    def create_table_users(self):
        """
        Create the 'users' table if it does not already exist.
        """
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS `users` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `user_id` bigint(200) NOT NULL UNIQUE,
                `status` VARCHAR(255) IN ('remove', 'active', 'blocked', 'ban', 'unban', 'sleep', 'active') DEFAULT 'active',
                `initiator_user_id` bigint(200),
                `updater_user_id` bigint(200),
                `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `language_code` varchar(5)
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
                    `channel_id` bigint(200),
                    `initiator_user_id` bigint(200),
                    `updater_user_id` bigint(200),
                    `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

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
                    `user_id` bigint(200) NOT NULL UNIQUE,
                    `initiator_user_id` bigint(200),
                    `updater_user_id` bigint(200),
                    `send_message` TINYINT(1) DEFAULT 0,
                    `statistika` TINYINT(1) DEFAULT 0,
                    `download_statistika` TINYINT(1) DEFAULT 0,
                    `block_user` TINYINT(1) DEFAULT 0,
                    `channel_settings` TINYINT(1) DEFAULT 0,
                    `add_admin` TINYINT(1) DEFAULT 0,
                    `set_data` TINYINT(1) DEFAULT 0,
                    `get_data` TINYINT(1) DEFAULT 0,
                    `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                `updater_user_id` bigint(200) NOT NULL UNIQUE,
                `initiator_user_id` bigint(200),
                `key` VARCHAR(255) NOT NULL,
                `value` VARCHAR(255) NOT NULL,
                `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    ## ------------------ Insert data ------------------ ##

    def insert_settings(self, initiator_user_id, key, value):
        """
        Add a setting to the 'settings' table.
        """
        try:
            sql = """
            INSERT INTO `settings` (`updater_user_id`, `initiator_user_id`, `key`, `value`) VALUES (%s, %s, %s, %s)
            """
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

            Parameters:
            user_id (int): The user's chat ID.
            language_code (str): The user's language_codeuage preference.
            """
            try:
                sql = """
                INSERT INTO `users` (`user_id`,`language_code`) VALUES (%s,%s)
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

        Parameters:
        channel_id (int): The channel's ID.
        initiator_user_id (int): The chat ID of the admin who added the channel.
        """
        try:
            sql = """
            INSERT INTO `channels` (`channel_id`, `initiator_user_id`) VALUES (%s,%s)
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

        Parameters:
        user_id (int): The admin's chat ID.
        initiator_user_id (int): The chat ID of the admin who added this admin.
        """
        try:
            sql = """
            INSERT INTO `admins` (`user_id`,`initiator_user_id`) VALUES (%s,%s)
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
        Parameters:
        updater_user_id (int): The chat ID of the admin who updated the setting.
        initiator_user_id (int): The chat ID of the admin who initiated the update.
        key (str): The key of the setting to be updated.
        value (str): The new value for the setting.
        """
        try:
            sql = """
            UPDATE `settings` SET `value`=%s, `updater_user_id`=%s,  WHERE `key`=%s
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

        Parameters:
        user_id (int): The admin's chat ID.
        column (str): The column to be updated.
        value (str): The new value for the specified column.
        updater_user_id (int): The chat ID of the admin who updated the data.
        Returns:
            None
        
        """
        try:
            sql = f"""UPDATE `admins` SET `{column}` = '{value}', `updater_user_id` = '{updater_user_id}' WHERE `user_id`=%s"""
            values = (user_id,)
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
        Parameters:
        user_id (int): The user's chat ID.
        status (str): The new status for the user.
        Returns:
           None
        """
        try: 
            sql = f"""UPDATE `users` SET `status` = '{status}', `updater_user_id` = '{updater_user_id}' WHERE `user_id`=%s"""
            values = (user_id,)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    ## ------------------ Select ------------------ ##

    # Select a setting from the 'settings' table.
    def select_setting(self, key: str):
        """
        Select a setting from the 'settings' table.
        Parameters:
        key (str): The key of the setting to retrieve.
        Returns:
        str: The value of the setting.
        """
        try:
            sql = "SELECT `value` FROM `settings` WHERE `key`=%s"
            values = (key,)
            self.cursor.execute(sql, values)
            result = self.cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    # Select all users from the 'ban' table.
    def select_all_users_ban(self):
        """
        Select all users from the 'users' table.

        Returns:
        list: A list of tuples containing all banned users.
        """
        try:
            sql = """
            SELECT * FROM `users` WHERE `status`='ban'`
            """
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

        Returns:
        int: The total number of banned users.
        """
        try:
            sql = "SELECT COUNT(*) FROM `users` WHERE `status`='ban'`;"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    def check_user_ban(self, user_id):
        """
        Check if a user is banned.

        Parameters:
        user_id (int): The user's chat ID.

        Returns:
        tuple: The user's ban information if they are banned, None otherwise.
        """
        try:
            self.cursor.execute("SELECT * FROM `users` WHERE `status`='ban' AND `user_id`=%s", (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    def delete_user_ban(self, user_id):
        """
        Delete a user from the 'ban' table.

        Parameters:
        user_id (int): The user's chat ID.
        """
        try:
            self.cursor.execute("DELETE FROM `ban` WHERE `user_id`=%s", (user_id,))
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    # Select all users from the 'users' table.
    def select_all_users(self):
        """
        Select all users from the 'users' table.

        Returns:
        list: A list of tuples containing all users.
        """
        try:
            sql = """
            SELECT * FROM `users`
            """
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
        Select user from the 'users' table on id.

        :param start_id: The start ID (integer).
        :param end_id: The end ID (integer).

        :return list: A list of tuples containing all users.
        """
        try:
            sql = "SELECT * FROM `users` WHERE `id` >= %s AND `id` < %s;"
            value = (start_id, end_id)
            self.cursor.execute(sql, value)
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

        Returns:
        int: The total number of users.
        """
        try:
            sql = "SELECT COUNT(*) FROM `users`;"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    def check_user(self, user_id):
        """
        Check if a user exists in the 'users' table.

        Parameters:
        user_id (int): The user's chat ID.

        Returns:
        tuple: The user's information if they exist, None otherwise.
        """
        try:
            self.cursor.execute("SELECT * FROM `users` WHERE `user_id`=%s", (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    # Select admin from admins table
    def select_admin_column(self, user_id, column):
        """
        Select a specific column for an admin from the 'admins' table.

        Parameters:
        user_id (int): The admin's chat ID.
        column (str): The column to be selected.

        Returns:
        any: The value of the specified column for the admin.
        """
        try:
            self.cursor.execute(f"SELECT {column} FROM `admins` WHERE `user_id`=%s", (user_id,))
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

        Parameters:
        user_id (int): The admin's chat ID.

        Returns:
        tuple: The admin's information if they exist, None otherwise.
        """
        try:
            self.cursor.execute("SELECT * FROM `admins` WHERE `user_id`=%s LIMIT 1", (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    def select_add_admin(self, user_id):
        """
        Select all admins added by a specific admin from the 'admins' table.

        Parameters:
        user_id (int): The chat ID of the admin who added other admins.

        Returns:
        list: A list of tuples containing the added admins' information.
        """
        try:
            self.cursor.execute("SELECT * FROM `admins` WHERE `initiator_user_id`=%s", (user_id,))
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

        Returns:
        list: A list of tuples containing all admins' information.
        """
        try:
            sql = """
            SELECT * FROM `admins`
            """
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

        Returns:
        int: The total number of admins.
        """
        try:
            sql = "SELECT COUNT(*) FROM `admins`"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    def delete_admin(self, user_id):
        """
        Delete an admin from the 'admins' table.

        Parameters:
        user_id (int): The admin's chat ID.
        """
        try:
            self.cursor.execute("DELETE FROM `admins` WHERE `user_id`=%s", (user_id,))
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    # Select channels from the 'channels' table
    def select_channels(self):
        """
        Select all channels from the 'channels' table.

        Returns:
        list: A list of tuples containing all channels' information.
        """
        try:
            self.cursor.execute("SELECT * FROM `channels`")
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    def select_channels_initiator_user_id(self, initiator_user_id):
        """
        Select all channels added by a specific admin from the 'channels' table.

        Parameters:
        initiator_user_id (int): The chat ID of the admin who added the channels.

        Returns:
        list: A list of tuples containing the added channels' information.
        """
        try:
            self.cursor.execute("SELECT * FROM `channels` WHERE `initiator_user_id`=%s", (initiator_user_id,))
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    def check_channel(self, user_id):
        """
        Check if a channel exists in the 'channels' table.

        Parameters:
        user_id (int): The channel's ID.

        Returns:
        tuple: The channel's information if it exists, None otherwise.
        """
        try:
            self.cursor.execute("SELECT * FROM `channels` WHERE `user_id`=%s", (user_id,))
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

        Returns:
        list: A list of tuples containing all channels' information.
        """
        try:
            sql = """
            SELECT * FROM `channels`
            """
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)


    ## -------------- Delete -------------- ##

    def delete_channel(self, user_id):
        """
        Delete a channel from the 'channels' table.

        Parameters:
        user_id (int): The channel's ID.
        """
        try:
            self.cursor.execute("DELETE FROM `channels` WHERE `channel_id`=%s", (user_id,))
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)
