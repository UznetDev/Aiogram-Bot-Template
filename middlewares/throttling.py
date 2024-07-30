import logging
import time
from keyboards.inline.close_btn import close_btn
from aiogram import BaseMiddleware, types
from aiogram.dispatcher.event.handler import HandlerObject
from loader import bot
from function.translator import translator

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, default_rate: int = 0.5) -> None:
        self.limiters = {}
        self.default_rate = default_rate
        self.count_throttled = 1
        self.last_throttled = 0

    async def __call__(self, handler, event: types.Message, data):
        real_handler: HandlerObject = data["handler"]
        skip_pass = True
        if event.message:
            user_id = event.message.from_user.id
            lang = event.message.from_user.language_code
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            lang = event.callback_query.from_user.language_code
        else:
            lang = 'en'

        if real_handler.flags.get("skip_pass") is not None:
            skip_pass = real_handler.flags.get("skip_pass")

        if skip_pass:
            if int(time.time()) - self.last_throttled >= self.default_rate:
                self.last_throttled = int(time.time())
                self.default_rate = 0.5
                self.count_throttled = 0
                return await handler(event, data)
            else:
                if self.count_throttled >= 2:
                    self.default_rate = 3
                else:
                    try:
                        self.count_throttled += 1
                        tx = translator(text='Many requests have been made',
                                        dest=lang)
                        try:
                            await event.callback_query.answer(tx)
                        except:
                            await bot.send_message(chat_id=user_id,
                                                   text=tx,
                                                   reply_markup=close_btn())
                    except Exception as err:
                        logging.error(err)





            self.last_throttled = int(time.time())
        else:
            return await handler(event, data)