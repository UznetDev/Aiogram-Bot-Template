import bot.handlers
import logging
from bot.loader import * 
from bot.utils.notify_admins import on_startup_notify
from bot.utils.set_bot_commands import set_default_commands
from bot.db.database import MySQLHandler


async def main():
    await on_startup_notify()
    await set_default_commands()

    try:
        # middlewares
        SM.update(key='test', value='test')
        print(db.select_setting('test'))
        if FM.feature('middlewares'):
            from bot.middlewares.throttling import ThrottlingMiddleware
            dp.update.middleware.register(ThrottlingMiddleware(db=db, bot=bot))


        if FM.feature('save_log'):
            mysql_handler = MySQLHandler(bot=bot, connection=db.connection)
            root_logger.addHandler(mysql_handler)
            
        mandatory_membership = db.select_setting('mandatory_membership')
        if mandatory_membership is None:
            db.insert_settings(initiator_user_id=1, key='mandatory_membership', value='False')

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        res = db.stat()
        logging.info(res)
        await bot.session.close()



    

