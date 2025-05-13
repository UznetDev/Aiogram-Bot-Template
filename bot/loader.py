import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from redis import Redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.bot import DefaultBotProperties  # Yangi versiyadagi default sozlamalar uchun
from bot.data.config import *
from bot.db.database import Database
from bot.api.translator import Translator
from bot.core.feature_manager import FeatureManager


# MySQL ma'lumotlar bazasi ulanishini yaratamiz
db = Database(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

log_format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

redis = Redis(host="localhost", port=6379, db=0, decode_responses=True)

FM = FeatureManager(db=db, root_logger=root_logger, redis_client=redis)


# Botni token va default parametr orqali yaratamiz
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Xotira asosidagi storage ni yaratamiz
storage = RedisStorage(redis=redis)

# Dispatcher obyektini yaratishda bot va storage ni uzatamiz
dp = Dispatcher(bot=bot, storage=storage)

# Router obyektini yaratamiz
router = Router()


translator = Translator(db=db, FM=FM)







