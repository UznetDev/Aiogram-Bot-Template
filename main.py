import middlewares, handlers  # Import middlewares and handlers modules
import asyncio
import sys
from utils.notify_admins import on_startup_notify  # Import the function to notify admins on startup
import logging
from utils.set_bot_commands import set_default_commands  # Import the function to set default bot commands
from loader import *  # Import all from loader module
from middlewares import ThrottlingMiddleware  # Import the ThrottlingMiddleware class
from data.config import log_file_name  # Import the log file name from config


async def main():
    """
    The main asynchronous function to start the bot and perform initial setup.
    """
    await on_startup_notify()  # Notify admins about the bot startup
    await set_default_commands()  # Set the default commands for the bot
    dp.update.middleware.register(ThrottlingMiddleware())  # Register the ThrottlingMiddleware

    try:
        # Try to create necessary database tables
        try:
            file_db.add_data(False, key='ads')
            db.create_table_admins()  # Create the admins table
            db.create_table_ban()  # Create the ban table
            db.create_table_users()  # Create the users table
            db.create_table_channel()  # Create the channel table
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
    # Configure logging
    format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        filename=log_file_name,  # Save error log on file
        level=logging.ERROR,  # Set the logging level to INFO
        format=format,  # Set the logging format
        # stream=sys.stdout  # Log to stdout
    )
    # Run the main function asynchronously
    asyncio.run(main())

