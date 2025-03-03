# cython: language_level=3
import logging
import time
from keyboards.inline.close_btn import close_btn
from aiogram import BaseMiddleware, types
from loader import bot, db
from function.translator import translator

# E'tibor bering: BaseMiddleware toza Python klassi, shuning uchun cdef class emas.
class ThrottlingMiddleware(BaseMiddleware):
    """
    So'rovlarni cheklash (throttling) orqali tizim yuklanishini kamaytiruvchi middleware.
    Agar foydalanuvchi 1 daqiqa ichida 3 marta "Many requests have been made" xabarini olsa,
    u 1 soatga ban qilinadi.
    """
    def __init__(self, default_rate: float = 0.5) -> None:
        """
        Middleware'ni boshlang'ich sozlamalar bilan yaratadi.
        
        Parameters:
          default_rate (float): So'rovlar oralig'idagi minimal vaqt (sekundlarda), default 0.5 sekund.
        """
        self.limiters = {}  # Foydalanuvchi ID bo'yicha throttling ma'lumotlari
        self.default_rate = default_rate

    async def __call__(self, handler, event: types.Message, data):
        """
        So'rovlarni qabul qilib, throttling qoidalarini bajarsa, keyingi handlerga o'tadi.
        Agar foydalanuvchi 1 daqiqa ichida 3 marta throttlingga tushsa, u 1 soatga ban qilinadi.
        """
        # real_handler-ni oddiy Python obyekti sifatida olamiz, uni C tip sifatida belgilashga hojat yo'q
        real_handler = data["handler"]
        skip_pass = True

        # Foydalanuvchi identifikatori va tilini aniqlaymiz
        if event.message:
            user_id = event.message.from_user.id
            lang = event.message.from_user.language_code
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            lang = event.callback_query.from_user.language_code
        else:
            lang = 'en'
            return await handler(event, data)

        if real_handler.flags.get("skip_pass") is not None:
            skip_pass = real_handler.flags.get("skip_pass")

        now = time.time()
        # Har bir foydalanuvchi uchun: "last": oxirgi so'rov vaqti, "count": throttled holatlar soni, "first": oynaning boshlanish vaqti
        user_data = self.limiters.get(user_id, {"last": now, "count": 0, "first": now})

        if skip_pass:
            if now - user_data["last"] >= self.default_rate:
                user_data["last"] = now
                user_data["count"] = 0  # Hisobni tiklash
                user_data["first"] = now
                self.limiters[user_id] = user_data
                return await handler(event, data)
            else:
                if now - user_data["first"] > 60:
                    user_data["count"] = 0
                    user_data["first"] = now
                user_data["count"] += 1

                if user_data["count"] >= 3:
                    try:
                        db.ban_user_for_one_hour(user_id)
                        tx = translator(
                            text='You have been banned for 1 hour due to too many requests.',
                            dest=lang
                        )
                        await bot.send_message(chat_id=user_id, text=tx)
                    except Exception as err:
                        logging.error("Error banning user %d: %s", user_id, err)
                    user_data["count"] = 0
                else:
                    try:
                        tx = translator(text='Many requests have been made', dest=lang)
                        try:
                            await event.callback_query.answer(tx)
                        except Exception:
                            await bot.send_message(
                                chat_id=user_id,
                                text=tx,
                                reply_markup=close_btn()
                            )
                    except Exception as err:
                        logging.error(err)

                user_data["last"] = now
                self.limiters[user_id] = user_data
                return
        else:
            return await handler(event, data)
