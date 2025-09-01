import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.bot import DefaultBotProperties
from bot.data.config import *
from bot.db.database import Database
from bot.api.translator import Translator
from bot.core.feature_manager import FeatureManager
from bot.core.settings_manager import SettingsManager
from bot.core.admin_rights_manager import AdminsManager
from bot.core.manage_mandatory_membership import ManageMandatoryMembership



root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)


db = Database(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE, root_logger=root_logger)





log_format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

redis = Redis(host="localhost", port=6379, db=5, decode_responses=True)
async_redis = AsyncRedis(host="localhost", port=6379, db=1, decode_responses=True)



bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

storage = RedisStorage(redis=async_redis)

dp = Dispatcher(bot=bot, storage=storage)

router = Router()


FM = FeatureManager(db=db, root_logger=root_logger, redis_client=redis)
AM = AdminsManager(db=db, redis_client=redis, root_logger=root_logger)
SM = SettingsManager(db=db, redis_client=redis, root_logger=root_logger)

translator = Translator(db=db, FM=FM, root_logger=root_logger, redis_client=redis)


MMM = ManageMandatoryMembership(db=db, redis_client=redis)
