import datetime
from environs import Env


# Initialize the Env object to read environment variables
env = Env()
env.read_env()

# Read environment variables for bot configuration
BOT_TOKEN = env.str("BOT_TOKEN")  # The token for the Telegram bot
ADMIN = env.int("ADMIN")  # The ID of the super admin
HOST = env.str('HOST')  # The host for the database
MYSQL_USER = env.str('MYSQL_USER')  # The MySQL database user
MYSQL_PASSWORD = env.str('MYSQL_PASSWORD')  # The MySQL database password
MYSQL_DATABASE = env.str('MYSQL_DATABASE')  # The MySQL database name

# Get the current date and time
datas = datetime.datetime.now()
yil_oy_kun = datetime.datetime.date(datetime.datetime.now())  # The current date (year-month-day)
soat_minut_sekund = f"{datas.hour}:{datas.minute}:{datas.second}"  # The current time (hour:minute:second)

# Define the log file name and path
log_file_name = 'db/logging.log'  # The log file path for logging database activities


# Date and time
datas = datetime.datetime.now()
date_day_month = (datetime.datetime.date(datetime.datetime.now()))
time_hour_minute_second = f"{datas.hour}:{datas.minute}:{datas.second}"