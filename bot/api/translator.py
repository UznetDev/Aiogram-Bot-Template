import logging
from typing import Optional
from deep_translator import GoogleTranslator

from bot.db.database import Database
from bot.function.function import to_hash
from bot.core.feature_manager import FeatureManager


class Translator:
    def __init__(self, db: Database,
                 FM: FeatureManager,
                 root_logger: logging.Logger,
                 default_dest: str = "en",
                 default_src: str = "en"):
        self.db: Database = db
        self.root_logger = root_logger
        self.default_dest = default_dest
        self.default_src = default_src
        self.FM: FeatureManager = FM
        self.create_table_translations()
        self.create_table_texts()

    def __call__(
        self,
        text: str,
        dest: Optional[str] = None,
        src: Optional[str] = None,
    ) -> str:
        return self.translate(text, dest=dest, src=src)

    def translate(self,
                 text: str,
                 dest: Optional[str] = 'en',
                 src: Optional[str] = 'en') -> str:
        try:
            if self.FM.feature('translator'):
                if dest == src or not text:
                    return text
                dest = dest or self.default_dest
                src  = src or self.default_src


                hash_value = to_hash(text)
                hash_index = self.select_texts(hash_value)
                if hash_index:
                    check = self.select_translations(hash_index, dest)
                    if check:
                        return check
                    else:
                        translated = GoogleTranslator(source=src, target=dest).translate(text)
                        self.insert_translations(text_id=hash_index, dest_lang=dest, translated_content=translated)
                        return translated
                else:
                    hash_index = self.insert_texts(hash_value=hash_value, raw_text=text)
                    translated = GoogleTranslator(source=src, target=dest).translate(text)
                    self.insert_translations(text_id=hash_index, dest_lang=dest, translated_content=translated)
                    return translated
            else:
                return text
        except Exception as e:
            self.root_logger.info(f"Error in translator.py: {e}")
            return text
        
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
            self.db.cursor.execute(sql)
            self.db.connection.commit()
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
            self.db.cursor.execute(sql)
            self.db.connection.commit()
        except Exception as err:
            self.root_logger.error(err)

    def insert_texts(self, hash_value: str, raw_text: str):
        try:
            sql = "INSERT INTO `texts` (`hash_value`, `raw_text`) VALUES (%s, %s)"
            values = (hash_value, raw_text)
            self.db.cursor.execute(sql, values)
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Exception as err:
            self.root_logger.error(err)

    def insert_translations(self, text_id: int, dest_lang: str, translated_content: str):
        try:
            sql = "INSERT INTO `translations` (`text_id`, `dest_lang`, `translated_content`) VALUES (%s, %s, %s)"
            values = (text_id, dest_lang, translated_content)
            self.db.cursor.execute(sql, values)
            self.db.connection.commit()
        except Exception as err:
            self.root_logger.error(err)

    def select_texts(self, hash_value: str):
        try:
            sql = "SELECT * FROM `texts` WHERE `hash_value` = %s LIMIT 1"
            values = (hash_value,)
            self.db.cursor.execute(sql, values)
            result = self.db.cursor.fetchone()
            return None if result is None else result['id']
        except Exception as err:
            self.root_logger.error(err)

    def select_translations(self, text_id: int, dest_lang: str):
        try:
            sql = "SELECT * FROM `translations` WHERE `text_id` = %s AND `dest_lang` = %s LIMIT 1"
            values = (text_id, dest_lang)
            self.db.cursor.execute(sql, values)
            result = self.db.cursor.fetchone()
            return None if result is None else result['translated_content']
        except Exception as err:
            self.root_logger.error(err)
