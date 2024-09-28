import asyncio
import logging
import handlers  # Import middlewares and handlers modules
from loader import *  # Import all from loader module
from utils.notify_admins import on_startup_notify  # Import the function to notify admins on startup
from utils.set_bot_commands import set_default_commands # Import the function to set default bot commands
from middlewares import ThrottlingMiddleware  # Import the ThrottlingMiddleware class
from middlewares.execution_time_middleware import ExecutionTimeMiddleware
from data.config import log_file_name  # Import the log file name from config
from utils.safe_formatter import SafeFormatter
from utils.db_api.mysql_handler import MySQLHandler  # Import the custom MySQLHandler


async def main():
    """
    The main asynchronous function to start the bot and perform initial setup.
    """
    await on_startup_notify()  # Notify admins about the bot startup
    await set_default_commands()  # Set the default commands for the bot
    dp.update.middleware.register(ThrottlingMiddleware())  # Register the ThrottlingMiddleware
    # dp.update.middleware.register(ExecutionTimeMiddleware())  # Register the ExecutionTimeMiddleware

    try:
        # Try to create necessary database tables
        try:
            file_db.add_data(False, key='ads')
            db.create_table_admins()  # Create the admins table
            db.create_table_ban()  # Create the ban table
            db.create_table_users()  # Create the users table
            db.create_table_channel()  # Create the channel table
        except Exception as err:
            logger = logging.getLogger(__name__)
            logger.error(err)  # Log any errors that occur during table creation

        # Delete any existing webhook and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    finally:
        # Log the database statistics and close the bot session
        res = db.stat()  # Get database statistics
        logger = logging.getLogger(__name__)
        logger.info(res)  # Log the database statistics
        await bot.session.close()  # Close the bot session

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Define log format with execution_time, chat_id, language_code
    # log_format = '  - %(message)s'
    log_format = '%(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s - %(name)s - %(chat_id)s - %(language_code)s - %(execution_time).6f  - %(asctime)s'

    formatter = SafeFormatter(log_format)

    # FileHandler for log file
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # StreamHandler for console logging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # MySQLHandler for logging to MySQL
    mysql_handler = MySQLHandler(
        host=HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        table='logs'
    )
    mysql_handler.create_table()
    mysql_handler.setFormatter(formatter)
    logger.addHandler(mysql_handler)

    asyncio.run(main())
