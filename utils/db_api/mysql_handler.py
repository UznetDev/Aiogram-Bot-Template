import logging
import mysql.connector
from mysql.connector import Error
import datetime
import sys


class MySQLHandler(logging.Handler):
    def __init__(self, host, user, password, database, table='logs'):
        super().__init__()
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.table = table
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """
        MySQL bazasiga ulanish va kerakli jadvalni yaratish.
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
            self.create_table()
        except Error as e:
            logging.error(f"MySQL-ga ulanishda xato: {e}")
            self.connection = None

    def create_table(self):
        """
        Log ma'lumotlarini saqlash uchun jadvalni yaratish.
        """
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS `{self.table}` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `created` DATETIME NOT NULL,
            `level` VARCHAR(10) NOT NULL,
            `filename` VARCHAR(255) NOT NULL,
            `funcName` VARCHAR(255) NOT NULL,
            `lineno` INT NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            `levelname` VARCHAR(50) NOT NULL,
            `message` TEXT NOT NULL,
            `chat_id` BIGINT NULL,
            `language_code` VARCHAR(10) NULL
        )
        """
        self.cursor.execute(create_table_sql)

    def emit(self, record):
        """
        Log yozuvlarini MySQL bazasiga yozish.
        """
        if self.connection is None:
            self.connect()
        if self.connection is None:
            return  # Ulanish muvaffaqiyatsiz bo'lsa, chiqish

        try:
            # Record'ni formatlash
            self.format(record)

            # Log ma'lumotlarini olish
            if self.formatter:
                created = self.formatter.formatTime(record, "%Y-%m-%d %H:%M:%S")
            else:
                # Agar formatter mavjud bo'lmasa, datetime modulidan foydalanamiz
                created = datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

            level = record.levelname
            filename = record.filename
            funcName = record.funcName
            lineno = record.lineno
            name = record.name
            levelname = record.levelname
            message = record.getMessage()
            chat_id = getattr(record, 'chat_id', None)
            language_code = getattr(record, 'language_code', None)

            sql = f"""
            INSERT INTO `{self.table}` 
            (`created`, `level`, `filename`, `funcName`, `lineno`, `name`, `levelname`, `message`, `chat_id`, `language_code`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (created, level, filename, funcName, lineno, name, levelname, message, chat_id, language_code)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except Exception as e:
            # Xatolik yuzaga kelsa, uni to'g'ridan-to'g'ri konsolga chiqaramiz
            print(f"MySQL-ga log yozishda xato: {e}", file=sys.stderr)
            # Xatoni qayta ko'tarish (ixtiyoriy)
            # raise
            # Yoki handleError funksiyasidan foydalanish
            self.handleError(record)