import bot.handlers
import logging
from bot.loader import * 
from bot.utils.notify_admins import on_startup_notify  # Import the function to notify admins on startup
from bot.utils.set_bot_commands import set_default_commands  # Import the function to set default bot commands
from bot.db.database import MySQLHandler


async def main():
    """
    The main asynchronous function to start the bot and perform initial setup.
    """
    await on_startup_notify()
    await set_default_commands()  # Set the default commands for the bot

    try:
        # middlewares
        if FM.feature('middlewares'):
            from bot.middlewares.throttling import ThrottlingMiddleware
            dp.update.middleware.register(ThrottlingMiddleware(db=db, bot=bot))  # Register the ThrottlingMiddleware


        # save_log
        if FM.feature('save_log'):
            mysql_handler = MySQLHandler(bot=bot, connection=db.connection)
            # log_format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
            # formatter = logging.Formatter(log_format)
            root_logger.addHandler(mysql_handler)
            
        mandatory_membership = db.select_setting('mandatory_membership')
        if mandatory_membership is None:
            db.insert_settings(initiator_user_id=1, key='mandatory_membership', value='False')

        # Delete any existing webhook and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        # Log the database statistics and close the bot session
        res = db.stat()  # Get database statistics
        logging.info(res)  # Log the database statistics
        await bot.session.close()  # Close the bot session



    

