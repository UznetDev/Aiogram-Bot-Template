import logging
from loader import dp, bot, db
from aiogram import types
from cython_code.user_check import User_Check
from function.translator import translator
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.inline.button import MainCallback
from data.config import date_day_month, time_hour_minute_second


@dp.message(User_Check())
async def start_handler(msg: types.Message):
    """
    Handles the text to check if the user has joined the required channels.
    If the user has not joined, provides a list of channels and their invitation links.

    Args:
        msg (types.Message): The message from the user.

    Returns:
        None
    """
    try:
        user_id = msg.from_user.id
        language_code = msg.from_user.language_code

        # Retrieve the list of channels from the database
        channels_list = db.select_channels()

        # Initialize the keyboard and message text
        keyboard = InlineKeyboardBuilder()
        message_text = translator(text="🛑 You have not joined the channel(s)!:\n\n", dest=language_code)
        count = 0

        # Iterate through the channels
        for x in channels_list:
            channel_id = str(-100) + str(x[1])
            channel = await bot.get_chat(channel_id)

            try:
                chat_member_status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
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
        await msg.answer(text=f"<b>{message_text}</b>", reply_markup=keyboard.as_markup())

        # Add user to the database if not already present
        if db.check_user(cid=user_id) is None:
            db.add_user(cid=user_id,
                        date=f"{date_day_month} / {time_hour_minute_second}")
    except Exception as err:
        logging.error(f"Error in start_handler: {err}")


@dp.callback_query(User_Check())
async def start_callback_query(call: types.CallbackQuery):
    """
    Handles callback queries to check if the user has joined the required channels.
    Provides a list of channels and their invitation links if the user has not joined.

    Args:
        call (types.CallbackQuery): The callback query from the user.

    Returns:
        None
    """
    try:
        user_id = call.from_user.id
        language_code = call.from_user.language_code

        # Retrieve the list of channels from the database
        channels_list = db.select_channels()

        # Initialize the keyboard and message text
        keyboard = InlineKeyboardBuilder()
        message_text = translator(text="🛑 You have not joined the channel(s)!:\n\n", dest=language_code)
        message_text1 = translator(text="🛑 You have not joined the channel(s)!:\n\n", dest=language_code)
        count = 0

        # Iterate through the channels
        for x in channels_list:
            channel_id = str(-100) + str(x[1])
            channel = await bot.get_chat(channel_id)

            try:
                chat_member_status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
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
        await call.answer(text=message_text1, reply_markup=keyboard.as_markup())
        await bot.send_message(chat_id=user_id, text=f"<b>{message_text}</b>", reply_markup=keyboard.as_markup())
        await call.answer('You have not joined the channel(s).')
    except Exception as err:
        logging.error(f"Error in start_callback_query: {err}")

