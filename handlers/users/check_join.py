import logging
from loader import dp, bot, db
from aiogram import types, F
from function.translator import translator
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.inline.button import MainCallback


@dp.callback_query(MainCallback.filter(F.action == "check_join"))
async def check_join(call: types.CallbackQuery):
    """
    Handles the 'check_join' callback query to verify if the user has joined required channels.
    If the user has not joined, it provides a list of channels to join and their invitation links.

    Args:
        call (types.CallbackQuery): The callback query from the user.

    Returns:
        None
    """
    try:
        # Extract user ID and language code
        user_id = call.from_user.id
        language_code = call.from_user.language_code

        # Retrieve the list of channels from the database
        channels_list = db.select_channels()

        # Initialize the keyboard and message text
        keyboard = InlineKeyboardBuilder()
        message_text = translator(text="🛑 You have not joined the channel(s)!:\n\n", dest=language_code)
        count = 0
        has_unjoined_channels = False

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
                has_unjoined_channels = True
                count += 1
                message_text += f"\n{count}. ⭕ <b>{channel.full_name}</b> <i>@{channel.username} ❓</i>\n"
                keyboard.button(text='➕ ' + channel.title,
                                url=f"{await channel.export_invite_link()}")

        # Add a button to check again
        keyboard.button(text=translator(text='♻ Check!', dest=language_code),
                        callback_data=MainCallback(action="check_join", q='').pack())
        keyboard.adjust(1)

        # Send the appropriate message to the user
        if has_unjoined_channels:
            await call.answer(text=translator(text="🛑 You have not joined the channel(s)!", dest=language_code),
                              reply_markup=keyboard.as_markup())
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=call.message.message_id,
                                        text=f"<b>{message_text}</b>",
                                        reply_markup=keyboard.as_markup())
        else:
            text = translator(text='You are already a member of all required channels.', dest=language_code)
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=call.message.message_id,
                                        text=text)
    except Exception as err:
        logging.error(f"Error in check_join: {err}")

