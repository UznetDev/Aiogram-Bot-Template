import logging
from aiogram import BaseMiddleware
from loader import bot, db, DB
from data.config import ADMIN
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class User_Check(BaseFilter, BaseMiddleware):
    def __init__(self):
        self.ADMIN = ADMIN

    async def __call__(self, message: Message, call=CallbackQuery) -> bool:
        try:
            data = DB.reading_db()
            if data['join_channel']:
                try:
                    cid = message.from_user.id
                except Exception as err:
                    cid = call.from_user.id
                    logging.error(err)
                if cid != ADMIN:
                    force = False
                    result = db.select_channels()
                    for x in result:
                        try:
                            ids = str(-100) + str(x[1])
                            await bot.get_chat(ids)
                            try:
                                res = await bot.get_chat_member(chat_id=ids, user_id=cid)
                            except:
                                continue
                            if res.status == 'member' or res.status == 'administrator' or res.status == 'creator':
                                pass
                            else:
                                force = True
                        except Exception as err:
                            logging.error(err)
                    return force
                else:
                    return False
            else:
                return False
        except Exception as err:
            logging.error(err)
        return False
