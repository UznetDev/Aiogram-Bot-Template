import bot.handlers
import logging
from bot.loader import * 
from bot.data.config import ADMIN
from bot.utils.notify_admins import on_startup_notify
from bot.utils.set_bot_commands import set_default_commands
from bot.db.database import MySQLHandler


async def main():
    await on_startup_notify()
    await set_default_commands()

    try:

        admin_rights = [
            ('add_admin', 'Add admins.', 'Yangi adminlar qo\'shish imkoniyati.'),
            ('add_rights', 'Add rights.', 'Adminlar uchun qushimcha huqqu qushish.'),
            ('add_features', 'Add features', 'Bot uchun yangi imkoniyatlar qushish.'),
        ]
        
        for key, name, description in admin_rights:
            AM.update_features(key, ADMIN, name, description, True)

        # middlewares
        if FM.feature('middlewares'):
            from bot.middlewares.throttling import ThrottlingMiddleware
            dp.update.middleware.register(ThrottlingMiddleware(db=db, bot=bot))


        if FM.feature('save_log'):
            mysql_handler = MySQLHandler(bot=bot, connection=db.connection)
            root_logger.addHandler(mysql_handler)
            

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        res = db.stat()
        logging.info(res)
        await bot.session.close()



    

