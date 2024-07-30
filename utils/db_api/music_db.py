import logging
import mysql.connector


class MusicDatabase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.reconnect()


    def reconnect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=True
        )
        self.cursor = self.connection.cursor()

    def create_table(self):
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS music (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message_id INT,
                file_id VARCHAR(250),
                file_unique_id VARCHAR(50),
                duration INT,
                performer VARCHAR(200),
                subject VARCHAR(200),
                title VARCHAR(200),
                file_name VARCHAR(200),
                mime_type VARCHAR(100),
                file_size INT,
                view_count INT,
                like_count INT,
                dislike_count INT)
            """
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def create_like_table(self):
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS likes(
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT NOT NULL,
                music_id INT NOT NULL,
                likes INT DEFAULT 0,
                dis_like INT DEFAULT 0,
                FOREIGN KEY (music_id) REFERENCES music(id) ON DELETE CASCADE)"""
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def create_table_playlist(self):
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS playlist(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    music_id INT NOT NUll,
                    FOREIGN KEY (music_id) REFERENCES music(id) ON DELETE CASCADE)"""
            self.cursor.execute(sql)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def add_data(self, message_id, file_id, file_unique_id, duration, performer, subject, title, file_name, mime_type,
                 file_size):
        try:
            sql = """
            INSERT INTO `music`(`message_id`, `file_id`, `file_unique_id`, `duration`, `performer`, `subject`, `title`, `file_name`, `mime_type`, `file_size`) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            values = (
                message_id, file_id, file_unique_id, duration, performer, subject, title, file_name, mime_type,
                file_size)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def count_music(self):
        try:
            sql = "SELECT COUNT(*) FROM `music`;"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result[0]
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def check_music(self, file_unique_id):
        try:
            self.cursor.execute("SELECT * FROM `music` WHERE `file_unique_id`=%s",
                                (file_unique_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def search_music(self, text: str, limit=10, data='id, duration, file_size, performer, title'):
        try:
            text = text.strip()
            sql = f"""SELECT {data} FROM `music` 
                      WHERE CONCAT(title, ' ', performer, performer, ' ', title, performer, ' - ', title, title, ' - ', performer) LIKE %s
                      ORDER BY view_count DESC, like_count DESC, dislike_count, message_id DESC
                      LIMIT %s"""
            value = (f'%{text}%', limit)
            self.cursor.execute(sql, value)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def search_music_match(self, text: str, limit=10, data='id, duration, file_size, performer, title'):
        try:
            text = text.strip()
            sql = f"""SELECT {data} FROM music
                      WHERE MATCH(performer, title) AGAINST (%s IN NATURAL LANGUAGE MODE)
                      ORDER BY view_count DESC, like_count DESC, dislike_count, message_id DESC
                      LIMIT %s"""
            self.cursor.execute(sql, (text, limit))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def get_music(self, music_id: int):
        sql = "SELECT * FROM `music` WHERE id=%s"
        self.cursor.execute(sql, (music_id,))
        return self.cursor.fetchone()

    def add_playlist(self, user_id, music_id):
        try:
            sql = "INSERT INTO `playlist`(`user_id`, `music_id`) VALUES (%s, %s)"
            self.cursor.execute(sql, (user_id, music_id))
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def check_playlist(self, user_id, music_id):
        try:
            sql = "SELECT * FROM `playlist` WHERE user_id=%s AND music_id=%s"
            self.cursor.execute(sql, (user_id, music_id))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def get_playlist(self, user_id):
        try:
            sql = """SELECT m.id, m.duration, m.file_size, m.subject, p.id 
                     FROM playlist AS p 
                     INNER JOIN music AS m ON m.id=p.music_id 
                     WHERE p.user_id=%s
                     GROUP BY p.id 
                     ORDER BY p.id DESC"""
            self.cursor.execute(sql, (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def remove_playlist(self, user_id, music_id):
        try:
            sql = "DELETE FROM `playlist` WHERE user_id=%s AND music_id=%s"
            self.cursor.execute(sql, (user_id, music_id))
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def add_like(self, user_id, music_id, like, dislike):
        try:
            sql = "INSERT INTO `likes`(`user_id`, `music_id`, `likes`, `dis_like`) VALUES (%s,%s,%s,%s)"
            self.cursor.execute(sql, (user_id, music_id, like, dislike))
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def check_like(self, user_id, music_id):
        try:
            sql = "SELECT * FROM `likes` WHERE user_id=%s AND music_id=%s"
            self.cursor.execute(sql, (user_id, music_id))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def update_like(self, user_id, music_id, like, dislike):
        try:
            sql = "UPDATE `likes` SET `likes`=%s,`dis_like`=%s WHERE user_id=%s AND music_id=%s"
            self.cursor.execute(sql, (like, dislike, user_id, music_id))
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def update_music(self, view, like, dislike, music_id):
        try:
            sql = "UPDATE `music` SET `view_count`=%s, `like_count`=%s,`dislike_count`=%s WHERE id=%s"
            self.cursor.execute(sql, (view, like, dislike, music_id))
            self.connection.commit()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

    def __del__(self):
        try:
            self.connection.close()
        except mysql.connector.Error as err:
            logging.error(f"MySQL Error: {err}")
            self.reconnect()
        except Exception as err:
            logging.error(f"General Error: {err}")

