import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.bot import DefaultBotProperties  # Yangi versiyadagi default sozlamalar uchun
from data.config import *  # Konfiguratsiyalarni import qilamiz
from db.database import Database, MySQLHandler
from function.translator import Translator
from core.feature_manager import FeatureManager


# MySQL ma'lumotlar bazasi ulanishini yaratamiz
db = Database(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

log_format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)


FM = FeatureManager(db=db, root_logger=root_logger)

for feature in FEATURES:
    FM.feature(feature)


redis = Redis(host="localhost", port=6379, db=0, decode_responses=True)


# Botni token va default parametr orqali yaratamiz
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Xotira asosidagi storage ni yaratamiz
storage = RedisStorage(redis=redis)

# Dispatcher obyektini yaratishda bot va storage ni uzatamiz
dp = Dispatcher(bot=bot, storage=storage)

# Router obyektini yaratamiz
router = Router()


translator = Translator(db, FM=FM)

# middlewares
if FM.feature('middlewares'):
    from middlewares.throttling import ThrottlingMiddleware
    dp.update.middleware.register(ThrottlingMiddleware(db=db, bot=bot))  # Register the ThrottlingMiddleware


# save_log
if FM.feature('save_log'):
    mysql_handler = MySQLHandler(bot=bot, connection=db.connection)
    log_format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    root_logger.addHandler(mysql_handler)




