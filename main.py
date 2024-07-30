import middlewares, handlers
import asyncio
import sys
from utils.notify_admins import on_startup_notify
import logging
from utils.set_bot_commands import set_default_commands
from loader import *
from middlewares import ThrottlingMiddleware
from data.config import log_file_name



async def main():

    await on_startup_notify()
    await set_default_commands()
    dp.update.middleware.register(ThrottlingMiddleware())
    try:
        try:
            db.create_table_admins()
            db.create_table_ban()
            db.create_table_users()
            db.create_table_channel()
        except Exception as err:
            logging.error(err)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    finally:
        res = db.stat()
        logging.info(res)
        await bot.session.close()



if __name__ == "__main__":
    format = '%(filename)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s' # %(pathname)s -
    logging.basicConfig(#filename=log_file_name,
                        level=logging.INFO,
                        format=format,
                        stream=sys.stdout
                        )
    asyncio.run(main())
