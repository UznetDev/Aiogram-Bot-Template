# import asyncio
# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from aiogram import Bot, Dispatcher
# from bot.data.config import BOT_TOKEN
# from tests.unit.fakebot import FakeBot, FakeDispatcher
# from aiogram.fsm.storage.memory import MemoryStorage


# @pytest.fixture
# def bot():
#     return Bot(token=BOT_TOKEN, parse_mode="HTML")

# @pytest.fixture
# def dispatcher(bot):
#     storage = MemoryStorage()
#     return Dispatcher(bot=bot, storage=storage)



# # @pytest.fixture(scope="session")
# # def event_loop():
# #     loop = asyncio.get_event_loop_policy().new_event_loop()
# #     yield loop
# #     loop.close()
# # @pytest.fixture(autouse=True)
# # def patch_bot_and_dp(fake_bot):
# #     # bot.loader da asl bot va dp o‘rniga fake’larni o‘rnatamiz
# #     bot.loader.bot = fake_bot
# #     bot.loader.dp = FakeDispatcher(fake_bot)
# #     yield

# @pytest.fixture
# def fake_bot():
#     return FakeBot(username="test_bot")

# @pytest.fixture
# def dp(fake_bot):
#     # Bizning real `bot.loader.dp` o‘rniga FakeDispatcher ulanadi
#     return FakeDispatcher(fake_bot)

# @pytest.fixture
# def bot_token(monkeypatch):
#     monkeypatch.setenv("BOT_TOKEN", BOT_TOKEN)
#     return BOT_TOKEN

# @pytest.fixture
# def bot(bot_token):
#     return Bot(token=bot_token)

# @pytest.fixture
# def dp(bot):
#     """A fresh Dispatcher for each test (if you need it)."""
#     return Dispatcher()

# @pytest.fixture
# def bot_instance():
#     return Bot(token=BOT_TOKEN, parse_mode="HTML")



# # @pytest.fixture
# # def fake_db(monkeypatch):
# #     print("Creating fake DB")
# #     # class DummyDB:
#     #     def __init__(self):
#     #         self.texts = {}
#     #         self.translations = {}

#     #     def select_texts(self, hash_value):
#     #         return self.texts.get(hash_value)

#     #     def insert_texts(self, hash_value, text):
#     #         idx = len(self.texts) + 1
#     #         self.texts[hash_value] = idx
#     #         return idx

#     #     def select_translations(self, text_id, dest_lang):
#     #         return self.translations.get((text_id, dest_lang))

#     #     def insert_translations(self, text_id, dest_lang, translated_content):
#     #         self.translations[(text_id, dest_lang)] = translated_content

#     # db = DummyDB()

#     # monkeypatch.setattr("bot.db.database.Database", lambda *args, **kw: db)
#     # return db

# # @pytest.fixture
# # def feature_manager():
# #     class DummyFM:
# #         def feature(self, name): return True
# #     return DummyFM()

# # @pytest.fixture
# # def translator(fake_db, feature_manager):
# #     from bot.api.translator import Translator
# #     return Translator(db=fake_db, FM=feature_manager)
