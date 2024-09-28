import logging
import mysql.connector
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
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}", file=sys.stderr)

    def create_table(self):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS `{self.table}` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `created` DATETIME NOT NULL,
            `level_name` VARCHAR(50) NOT NULL,
            `filename` VARCHAR(255) NOT NULL,
            `funcName` VARCHAR(255) NOT NULL,
            `lineno` INT NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            `message` TEXT NOT NULL,
            `chat_id` BIGINT NULL,
            `language_code` VARCHAR(10) NULL,
            `execution_time` FLOAT NULL
        )
        """
        self.cursor.execute(create_table_sql)

    def emit(self, record):
        if self.connection is None:
            self.connect()
        if self.connection is None:
            return

        try:
            self.format(record)
            if record.filename == 'dispatcher.py' and record.funcName == 'feed_update' and record.lineno == 172:
                pass
            else:
                created = datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

                sql = f"""
                INSERT INTO `{self.table}` 
                (`created`, `level_name`, `filename`, `funcName`, `lineno`, `name`, `message`, `chat_id`, `language_code`, `execution_time`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    created, record.levelname, record.filename, record.funcName, record.lineno,
                    record.name, record.getMessage(),
                    getattr(record, 'chat_id', None),
                    getattr(record, 'language_code', None),
                    getattr(record, 'execution_time', None)
                )
                self.cursor.execute(sql, values)
                self.connection.commit()
        except Exception as e:
            print(f"Error writing to MySQL: {e}", file=sys.stderr)
            self.handleError(record)
