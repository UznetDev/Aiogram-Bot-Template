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
        Reconnect to the MySQL database. If the connection fails, log the error and attempt to reconnect.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def create_table_ban(self):
        """
        Create the 'ban' table if it does not already exist.
        """
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS ban (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cid bigint(20) NOT NULL UNIQUE,
                admin_cid bigint(20),
                date varchar(255)
            )
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def add_user_ban(self, cid, date, admin_cid):
        """
        Add a user to the 'ban' table.

        Parameters:
        cid (int): The user's chat ID.
        date (str): The date the user was banned.
        admin_cid (int): The admin's chat ID who banned the user.
        """
        try:
            sql = """
            INSERT INTO `ban` (`cid`,`admin_cid`,`date`) VALUES (%s,%s,%s)
            """
            values = (cid, admin_cid, date)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_all_users_ban(self):
        """
        Select all users from the 'ban' table.

        Returns:
        list: A list of tuples containing all banned users.
        """
        try:
            sql = """
            SELECT * FROM `ban`
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
            sql = "SELECT COUNT(*) FROM `ban`;"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def check_user_ban(self, cid):
        """
        Check if a user is banned.

        Parameters:
        cid (int): The user's chat ID.

        Returns:
        tuple: The user's ban information if they are banned, None otherwise.
        """
        try:
            self.cursor.execute("SELECT * FROM `ban` WHERE `cid`=%s", (cid,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def delete_user_ban(self, cid):
        """
        Delete a user from the 'ban' table.

        Parameters:
        cid (int): The user's chat ID.
        """
        try:
            self.cursor.execute("DELETE FROM `ban` WHERE `cid`=%s", (cid,))
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def create_table_users(self):
        """
        Create the 'users' table if it does not already exist.
        """
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cid bigint(20) NOT NULL UNIQUE,
                date varchar(255),
                lang varchar(5)
            )
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def add_user(self, cid, date, lang):
        """
        Add a user to the 'users' table.

        Parameters:
        cid (int): The user's chat ID.
        date (str): The date the user was added.
        lang (str): The user's language preference.
        """
        try:
            sql = """
            INSERT INTO `users` (`cid`,`date`,`lang`) VALUES (%s,%s,%s)
            """
            values = (cid, date, lang)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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

    def check_user(self, cid):
        """
        Check if a user exists in the 'users' table.

        Parameters:
        cid (int): The user's chat ID.

        Returns:
        tuple: The user's information if they exist, None otherwise.
        """
        try:
            self.cursor.execute("SELECT * FROM `users` WHERE `cid`=%s", (cid,))
            result = self.cursor.fetchone()
            return result
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
                CREATE TABLE IF NOT EXISTS admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cid bigint(20) NOT NULL UNIQUE,
                    add_cid bigint(20),
                    send_message TINYINT(1),
                    statistika TINYINT(1),
                    download_statistika TINYINT(1),
                    block_user TINYINT(1),
                    channel_settings TINYINT(1),
                    add_admin TINYINT(1),
                    date varchar(255)
                );
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def update_admin_data(self, cid, column, value):
        """
        Update an admin's data in the 'admins' table.

        Parameters:
        cid (int): The admin's chat ID.
        column (str): The column to be updated.
        value (str): The new value for the specified column.
        """
        try:
            sql = f"""UPDATE `admins` SET `{column}` = '{value}' WHERE `cid`=%s"""
            values = (cid,)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_admin_column(self, cid, column):
        """
        Select a specific column for an admin from the 'admins' table.

        Parameters:
        cid (int): The admin's chat ID.
        column (str): The column to be selected.

        Returns:
        any: The value of the specified column for the admin.
        """
        try:
            self.cursor.execute(f"SELECT {column} FROM `admins` WHERE `cid`=%s", (cid,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def add_admin(self, cid, date, add):
        """
        Add an admin to the 'admins' table.

        Parameters:
        cid (int): The admin's chat ID.
        date (str): The date the admin was added.
        add (int): The chat ID of the admin who added this admin.
        """
        try:
            sql = """
            INSERT INTO `admins` (`cid`,`add_cid`,`date`) VALUES (%s,%s,%s)
            """
            values = (cid, add, date)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_admin(self, cid):
        """
        Select an admin from the 'admins' table.

        Parameters:
        cid (int): The admin's chat ID.

        Returns:
        tuple: The admin's information if they exist, None otherwise.
        """
        try:
            self.cursor.execute("SELECT * FROM `admins` WHERE `cid`=%s", (cid,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def select_add_admin(self, cid):
        """
        Select all admins added by a specific admin from the 'admins' table.

        Parameters:
        cid (int): The chat ID of the admin who added other admins.

        Returns:
        list: A list of tuples containing the added admins' information.
        """
        try:
            self.cursor.execute("SELECT * FROM `admins` WHERE `add_cid`=%s", (cid,))
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

    def delete_admin(self, cid):
        """
        Delete an admin from the 'admins' table.

        Parameters:
        cid (int): The admin's chat ID.
        """
        try:
            self.cursor.execute("DELETE FROM `admins` WHERE `cid`=%s", (cid,))
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
                CREATE TABLE IF NOT EXISTS channels (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cid bigint(200),
                    date varchar(255),
                    add_cid int(200)
                );
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def add_channel(self, cid, date, add_cid):
        """
        Add a channel to the 'channels' table.

        Parameters:
        cid (int): The channel's ID.
        date (str): The date the channel was added.
        add_cid (int): The chat ID of the admin who added the channel.
        """
        try:
            sql = """
            INSERT INTO `channels` (`cid`,`date`,`add_cid`) VALUES (%s,%s,%s)
            """
            values = (cid, date, add_cid)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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

    def select_channels_add_cid(self, add_cid):
        """
        Select all channels added by a specific admin from the 'channels' table.

        Parameters:
        add_cid (int): The chat ID of the admin who added the channels.

        Returns:
        list: A list of tuples containing the added channels' information.
        """
        try:
            self.cursor.execute("SELECT * FROM `channels` WHERE `add_cid`=%s", (add_cid,))
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def check_channel(self, cid):
        """
        Check if a channel exists in the 'channels' table.

        Parameters:
        cid (int): The channel's ID.

        Returns:
        tuple: The channel's information if it exists, None otherwise.
        """
        try:
            self.cursor.execute("SELECT * FROM `channels` WHERE `cid`=%s", (cid,))
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

    def delete_channel(self, cid):
        """
        Delete a channel from the 'channels' table.

        Parameters:
        cid (int): The channel's ID.
        """
        try:
            self.cursor.execute("DELETE FROM `channels` WHERE `cid`=%s", (cid,))
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

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
