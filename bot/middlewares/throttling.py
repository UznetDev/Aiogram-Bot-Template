import time
import logging
from data.config import ADMIN
from keyboards.inline.close_btn import close_btn
from aiogram import BaseMiddleware, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.inline.button import MainCallback
from api.translator import translator


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware class to manage throttling of requests to prevent overloading.
    This middleware limits the rate of incoming requests from users.
    If a user exceeds the allowed request rate, they will receive a message indicating that they are making too many requests.
    If a user receives the throttling warning 3 times within 1 minute, they are banned for 1 hour.
    """

    def __init__(self, bot, db, default_rate: float = 0.5) -> None:
        """
        Initializes the ThrottlingMiddleware instance.

        Parameters:
        - default_rate (float): The minimal interval between allowed requests (in seconds), default is 0.5 seconds.
        """
        self.limiters = {}  # Dictionary to store per-user throttling data.
        self.default_rate = default_rate
        self.bot = bot
        self.db = db


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
            language_code = event.message.from_user.language_code
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            language_code = event.callback_query.from_user.language_code
        else:
            language_code = 'en'
            return await handler(event, data)


        if user_id == ADMIN:
            return await handler(event, data)

        user_data = self.db.check_user(user_id=user_id)
        if user_data:
            is_ban = await self.check_ban(user_data)
            if is_ban:
                return 
            is_member = await self.check_member(user_id=user_id, language_code=language_code)
            if is_member:
                return

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
                            self.db.ban_user_for_one_hour(user_id, comment="1 hour due to too many requests.")
                            tx = translator(
                                text='You have been banned for 1 hour due to too many requests.',
                                dest=language_code
                            )
                            await self.bot.send_message(chat_id=user_id, text=tx)
                        except Exception as err:
                            logging.error(f"Error banning user {user_id}: {err}")
                        # Reset the counter to oldindan qayta-ban qilishdan saqlanish uchun.
                        user_data["count"] = 0
                    else:
                        try:
                            tx = translator(text='Many requests have been made', dest=language_code)
                            try:
                                await event.callback_query.answer(tx)
                            except Exception:
                                await self.bot.send_message(
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
        else:
            self.db.insert_user(user_id=user_id, 
                           language_code=language_code)
            return await handler(event, data)


    async def check_ban(self, user_data):
        try:

            if user_data['status'] == 'ban':
                text = translator(text="🛑 You are banned!:\n"
                        "⚠ If you think this is a mistake, contact the admin.",
                    dest=user_data['language_code'])
                if user_data['initiator_user_id'] == 1 or user_data['initiator_user_id'] == 0:
                    text += f"\n\n<b>👮‍♂️ Admin: self.bot</b>\n "
                elif user_data['initiator_user_id'] is not None:
                    admin_info = await self.bot.get_chat(chat_id=user_data['updater_user_id'])
                    text += f"\n\n<b>👮‍♂️ Admin @{admin_info.username}</b>\n "
                if user_data['comment'] is not None:
                    text += f"\n<b>📝 Comment: {user_data['comment']}</b>\n"

                if user_data['ban_time'] is not None:
                    text += f"\n<b>📅 Ban time: {user_data['ban_time']}</b>\n"

                admins = await self.bot.get_chat(chat_id=ADMIN)

                text += f'<b>👩‍💻 Super admin @{admins.username}</b>\n'

                await self.bot.send_message(chat_id=user_data['user_id'], 
                                       text=f"<b>{text}</b>", 
                                       reply_markup=close_btn())
                return True
            else:
                return False
        except Exception as err:
            logging.error(err)
            return False
        

    async def check_member(self, user_id, language_code):
        try:
            is_mandatory = self.db.select_setting('mandatory_membership')
            if is_mandatory is None:
                self.db.update_settings_key(updater_user_id=1, key='mandatory_membership', value=False)
                return False
            elif is_mandatory == 'False':
                return False
            elif is_mandatory == 'True':
                try:
                    channels = self.db.select_channels()
                except Exception as err:
                    logging.error(f"Error selecting channels: {err}")
                    return False

                for channel in channels:
                    try:
                        chat_id = int("-100" + str(channel.get('channel_id')))
                        res = await self.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                        
                        if res.status not in ('member', 'administrator', 'creator'):
                            count = 0

                            keyboard = InlineKeyboardBuilder.dbuilder()
                            message_text = translator(text="🛑 You have not joined the channel(s)!:\n\n", dest=language_code)

                            for x in channels:
                                channel_id = str(-100) + str(x['channel_id'])
                                channel = await self.bot.get_chat(channel_id)

                                try:
                                    chat_member_status = await self.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                                except Exception as e:
                                    logging.error(f"Error getting chat member status: {e}")
                                    continue

                                # Check if the user is a member of the channel
                                if chat_member_status.status not in ('member', 'administrator', 'creator'):
                                    count += 1
                                    message_text += f"\n{count}. ⭕ <b>{channel.full_name}</b> <i>@{channel.username} ❓</i>\n"
                                    keyboard.button(text='➕ ' + channel.title,
                                                    url=f"{await channel.export_invite_link()}")

                                    # Add a button to check again
                                    keyboard.button(text=translator(text='♻ Check!', dest=language_code),
                                                    callback_data=MainCallback(action="check_join", q='').pack())
                                    keyboard.adjust(1)

                                    # Send the message to the user
                                    await self.bot.send_message(chat_id=user_id, 
                                                            text=f"<b>{message_text}</b>", 
                                                            reply_markup=keyboard.as_markup())
                            return True
                    except Exception as err:
                        logging.error(f"Error checking membership for channel {channel.get('channel_id')}: {err}")
                        continue

                # If all channels checked and no problems found, return False.
                return False

        except Exception as err:
            logging.error(err)
            return False