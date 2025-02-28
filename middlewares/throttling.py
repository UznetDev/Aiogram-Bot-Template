import logging
import time
from data.config import ADMIN
from keyboards.inline.close_btn import close_btn
from aiogram import BaseMiddleware, types
from aiogram.dispatcher.event.handler import HandlerObject
from loader import bot, db
from function.translator import translator


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware class to manage throttling of requests to prevent overloading.
    This middleware limits the rate of incoming requests from users.
    If a user exceeds the allowed request rate, they will receive a message indicating that they are making too many requests.
    If a user receives the throttling warning 3 times within 1 minute, they are banned for 1 hour.
    """

    def __init__(self, default_rate: float = 0.5) -> None:
        """
        Initializes the ThrottlingMiddleware instance.

        Parameters:
        - default_rate (float): The minimal interval between allowed requests (in seconds), default is 0.5 seconds.
        """
        self.limiters = {}  # Dictionary to store per-user throttling data.
        self.default_rate = default_rate


    async def __call__(self, handler, event: types.Message, data):
        """
        Processes incoming messages and enforces throttling rules.
        If a user triggers throttling 3 times in 1 minute, they will be banned for 1 hour.
        """
        real_handler = data["handler"]
        skip_pass = True

        # Determine user id and language code.
        if event.message:
            user_id = event.message.from_user.id
            lang = event.message.from_user.language_code
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            lang = event.callback_query.from_user.language_code
        else:
            lang = 'en'
            return await handler(event, data)

        if user_id == ADMIN:
            return await handler(event, data)

        if real_handler.flags.get("skip_pass") is not None:
            skip_pass = real_handler.flags.get("skip_pass")

        now = time.time()
        # For each user we track:
        # "last": timestamp of the last request,
        # "count": number of throttled events in the current window,
        # "first": start timestamp of the current 1-minute window.
        user_data = self.limiters.get(user_id, {"last": now, "count": 0, "first": now})

        if skip_pass:
            # If enough time has passed since the last request, reset the throttling counter.
            if now - user_data["last"] >= self.default_rate:
                user_data["last"] = now
                user_data["count"] = 0  # Reset counter.
                user_data["first"] = now
                self.limiters[user_id] = user_data
                return await handler(event, data)
            else:
                # Update the throttling counter. If the current window is over 60 seconds, reset it.
                if now - user_data["first"] > 60:
                    user_data["count"] = 0
                    user_data["first"] = now
                user_data["count"] += 1

                # Agar throttling hisobi 3 yoki undan ko'p bo'lsa, foydalanuvchini ban qilamiz.
                if user_data["count"] >= 3:
                    try:
                        db.ban_user_for_one_hour(user_id, comment="Too many requests")
                        tx = translator(
                            text='You have been banned for 1 hour due to too many requests.',
                            dest=lang
                        )
                        await bot.send_message(chat_id=user_id, text=tx)
                    except Exception as err:
                        logging.error(f"Error banning user {user_id}: {err}")
                    # Reset the counter to oldindan qayta-ban qilishdan saqlanish uchun.
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
