from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from data.config import *  # Import all configurations from the config module
from utils.db_api.mysql_db import Database
from cython_code.file_db import BotDb, FileDB

# Initialize the Telegram bot with the given token and parse mode set to HTML
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

# Initialize memory storage for the dispatcher
storage = MemoryStorage()

# Initialize the dispatcher with the memory storage
dp = Dispatcher(storage=storage)

# Initialize the MySQL database connection
db = Database(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)

# Initialize the BotDb with the specified JSON file
DB = BotDb(file='data/db.json')
file_db = FileDB(file='data/file_db.json')
