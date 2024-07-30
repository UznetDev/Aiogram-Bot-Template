import logging
import mysql.connector


class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.reconnect()

    def reconnect(self):
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
        try:
            self.cursor.execute("DELETE FROM `ban` WHERE `cid`=%s", (cid,))
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def create_table_users(self):
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

    def stat(self):
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
        try:
            self.cursor.execute("DELETE FROM `admins` WHERE `cid`=%s", (cid,))
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def create_table_channel(self):
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
        try:
            self.cursor.execute("DELETE FROM `channels` WHERE `cid`=%s", (cid,))
        except mysql.connector.Error as err:
            logging.error(err)
            self.reconnect()
        except Exception as err:
            logging.error(err)

    def __del__(self):
        try:
            self.connection.close()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")
