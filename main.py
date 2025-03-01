import middlewares, handlers  # Import middlewares and handlers modules
import asyncio
import sys
import os
from utils.notify_admins import on_startup_notify  # Import the function to notify admins on startup
import logging
from utils.set_bot_commands import set_default_commands  # Import the function to set default bot commands
from loader import *  # Import all from loader module
# from middlewares import ThrottlingMiddleware  # Import the ThrottlingMiddleware class
from middlewares.throttling import ThrottlingMiddleware  # Import the ThrottlingMiddleware class
from data.config import log_file_name  # Import the log file name from config


async def main():
    """
    The main asynchronous function to start the bot and perform initial setup.
    """
    await on_startup_notify()
    await set_default_commands()  # Set the default commands for the bot
    dp.update.middleware.register(ThrottlingMiddleware())  # Register the ThrottlingMiddleware

    try:
        # Try to create necessary database tables
        try:
            db.create_table_admins()  # Create the admins table
            db.create_table_users()  # Create the users table
            db.create_table_channel()  # Create the channel table
            db.create_table_settings()  # Create the settings table
            join_channel = db.select_setting('join_channel')
            if join_channel is None:
                db.insert_settings(initiator_user_id=1, key='join_channel', value='False')

        except Exception as err:
            logging.error(err)  # Log any errors that occur during table creation

        # Delete any existing webhook and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    finally:
        # Log the database statistics and close the bot session
        res = db.stat()  # Get database statistics
        logging.info(res)  # Log the database statistics
        await bot.session.close()  # Close the bot session


if __name__ == "__main__":

    if not os.path.exists('logs'):
        os.mkdir('logs')

    if not os.path.exists(log_file_name):
        with open(log_file_name, 'w') as f:
            pass

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    log_format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    asyncio.run(main())

    

