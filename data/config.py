import datetime
from environs import Env
from utils.db_api.bot_db import BotDb

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN = env.int("ADMIN")
HOST = env.str('HOST')
MYSQL_USER = env.str('MYSQL_USER')
MYSQL_PASSWORD = env.str('MYSQL_PASSWORD')
MYSQL_DATABASE = env.str('MYSQL_DATABASE')

datas = datetime.datetime.now()
yil_oy_kun = (datetime.datetime.date(datetime.datetime.now()))
soat_minut_sekund = f"{datas.hour}:{datas.minute}:{datas.second}"

DB = BotDb(file='db/db.json')
log_file_name = 'db/logging.log'