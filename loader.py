from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties  # Yangi versiyadagi default sozlamalar uchun
from data.config import *  # Konfiguratsiyalarni import qilamiz
from db.database import Database
from cython_code.file_db import BotDb, FileDB

# Botni token va default parametr orqali yaratamiz
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Xotira asosidagi storage ni yaratamiz
storage = MemoryStorage()

# Dispatcher obyektini yaratishda bot va storage ni uzatamiz
dp = Dispatcher(bot=bot, storage=storage)

# MySQL ma'lumotlar bazasi ulanishini yaratamiz
db = Database(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)

# JSON fayllar bilan ishlash uchun obyektlar
DB = BotDb(file='data/db.json')
file_db = FileDB(file='data/file_db.json')
