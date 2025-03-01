import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties  # Yangi versiyadagi default sozlamalar uchun
from data.config import *  # Konfiguratsiyalarni import qilamiz
from db.database import Database

# Botni token va default parametr orqali yaratamiz
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Xotira asosidagi storage ni yaratamiz
storage = MemoryStorage()

# Dispatcher obyektini yaratishda bot va storage ni uzatamiz
dp = Dispatcher(bot=bot, storage=storage)

# Router obyektini yaratamiz
router = Router()

# MySQL ma'lumotlar bazasi ulanishini yaratamiz
db = Database(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

log_format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)