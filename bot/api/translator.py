from typing import Optional
from deep_translator import GoogleTranslator
from db.database import Database
from function.function import to_hash
from core.feature_manager import FeatureManager


class Translator:
    def __init__(self, db: Database,
                 FM: FeatureManager = None,
                 default_dest: str = "en",
                 default_src: str = "en"):
        self.db = db
        self.default_dest = default_dest
        self.default_src = default_src
        self.FM = FM

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
        if self.FM.feature('translator'):
            if dest == src or not text:
                return text
            dest = dest or self.default_dest
            src  = src or self.default_src


            hash_value = to_hash(text)
            hash_index = self.db.select_texts(hash_value)
            if hash_index:
                check = self.db.select_translations(hash_index, dest)
                if check:
                    return check
                else:
                    translated = GoogleTranslator(source=src, target=dest).translate(text)
                    self.db.insert_translations(text_id=hash_index, dest_lang=dest, translated_content=translated)
                    return translated
            else:
                hash_index = self.db.insert_texts(hash_value=hash_value, text=text)
                translated = GoogleTranslator(source=src, target=dest).translate(text)
                self.db.insert_translations(text_id=hash_index, dest_lang=dest, translated_content=translated)
                return translated
        else:
            return text