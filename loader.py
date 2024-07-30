from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from data.config import *
from utils.db_api.mysql_db import Database


bot = Bot(token=BOT_TOKEN,
          parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

db = Database(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
