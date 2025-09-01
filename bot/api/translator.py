import logging
from typing import Optional

from redis import Redis, RedisError
from deep_translator import GoogleTranslator

from bot.db.database import Database
from bot.function.function import to_hash
from bot.core.feature_manager import FeatureManager


class Translator:
    _REDIS_HASH_TEXTS = "texts"
    _REDIS_HASH_TRANSLATIONS = "translations"

    def __init__(
        self,
        db: Database,
        FM: FeatureManager,
        root_logger: logging.Logger,
        redis_client: Redis,
        default_dest: str = "en",
        default_src: str = "en",
    ):
        self.db: Database = db
        self.redis: Redis = redis_client
        self.FM: FeatureManager = FM
        self.log = root_logger

        self.default_dest = default_dest
        self.default_src = default_src

        self._create_table_texts()
        self._create_table_translations()

    def __call__(
        self,
        text: str,
        dest: Optional[str] = None,
        src: Optional[str] = None,
    ) -> str:
        return self.translate(text, dest=dest, src=src)

    def translate(
        self,
        text: str,
        dest: Optional[str] = None,
        src: Optional[str] = None,
    ) -> str:
        if not self.FM.feature("translator") or not text:
            return text

        dest = (dest or self.default_dest).lower()
        src = (src or self.default_src).lower()
        if dest == src:
            return text

        h = to_hash(text)
        field_t = f"{h}:{dest}" 
        try:
            cached = self.redis.hget(self._REDIS_HASH_TRANSLATIONS, field_t)
            if cached:
                return cached.decode() if isinstance(cached, bytes) else cached
        except RedisError as err:
            self.log.warning(f"Redis unavailable (translations): {err}")

        text_id = self._select_text_id(h)
        if text_id:
            mysql_translation = self._select_translation(text_id, dest)
            if mysql_translation:
                self._cache_translation_redis(field_t, mysql_translation)
                return mysql_translation
        try:
            translated = GoogleTranslator(source=src, target=dest).translate(text)
        except Exception as err:
            self.log.error(f"GoogleTranslator error: {err}")
            return text
        if not text_id:
            text_id = self._insert_text(h, text)
        self._insert_translation(text_id, dest, translated)
        self._cache_translation_redis(field_t, translated)
        return translated

    def _cache_translation_redis(self, field: str, value: str) -> None:
        try:
            self.redis.hset(self._REDIS_HASH_TRANSLATIONS, field, value)
        except RedisError as err:
            self.log.warning(f"Redis cache write failed: {err}")

    def _insert_text(self, hash_value: str, raw_text: str) -> int:
        sql = "INSERT INTO texts (hash_value, raw_text) VALUES (%s, %s)"
        self._exec(sql, (hash_value, raw_text))
        return self.db.cursor.lastrowid

    def _insert_translation(self, text_id: int, dest_lang: str, translated: str) -> None:
        sql = (
            "INSERT INTO translations (text_id, dest_lang, translated_content) "
            "VALUES (%s, %s, %s)"
        )
        self._exec(sql, (text_id, dest_lang, translated))

    def _select_text_id(self, hash_value: str) -> Optional[int]:
        sql = "SELECT id FROM texts WHERE hash_value = %s LIMIT 1"
        row = self._fetchone(sql, (hash_value,))
        return row["id"] if row else None

    def _select_translation(self, text_id: int, dest_lang: str) -> Optional[str]:
        sql = (
            "SELECT translated_content FROM translations "
            "WHERE text_id = %s AND dest_lang = %s LIMIT 1"
        )
        row = self._fetchone(sql, (text_id, dest_lang))
        return row["translated_content"] if row else None

    def _exec(self, sql: str, params: tuple) -> None:
        try:
            self.db.cursor.execute(sql, params)
            self.db.connection.commit()
        except Exception as err:
            self.log.error(err)

    def _fetchone(self, sql: str, params: tuple):
        try:
            self.db.cursor.execute(sql, params)
            return self.db.cursor.fetchone()
        except Exception as err:
            self.log.error(err)

    def _create_table_texts(self):
        sql = """
            CREATE TABLE IF NOT EXISTS texts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hash_value BIGINT UNSIGNED,
                raw_text TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP NULL DEFAULT NULL,
                INDEX(hash_value)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self._exec(sql, ())

    def _create_table_translations(self):
        sql = """
            CREATE TABLE IF NOT EXISTS translations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text_id INT NOT NULL,
                dest_lang CHAR(5) NOT NULL,
                translated_content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP NULL DEFAULT NULL,
                FOREIGN KEY (text_id) REFERENCES texts(id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self._exec(sql, ())
