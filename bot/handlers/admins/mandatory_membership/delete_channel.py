import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from api.translator import translator
from data.config import ADMIN

@dp.callback_query(IsAdmin(), AdminCallback.filter(F.action == "delete_channel"))
async def delete_channel(call: types.CallbackQuery, callback_data: AdminCallback, state: FSMContext):
    try:
        user_id = call.from_user.id  # The ID of the admin making the request
        mid = call.message.message_id  # The ID of the message associated with the callback
        language_code = call.from_user.language_code  # The language code for translating responses
        data = SelectAdmin(user_id=user_id)  # Check if the user has admin permissions
        btn = close_btn()  # A button for closing the message

        if data.channel_settings():
            ch_user_id = callback_data.data  # Channel ID from the callback data
            ch_user_id100 = str(-100) + str(ch_user_id)  # Format channel ID for API
            check = db.check_channel(user_id=ch_user_id)  # Check if the channel exists in the database

            if not check:
                # Inform the user if the channel does not exist
                text = translator(
                    text='⭕ Channel not found!\nThe channel seems to have been deleted previously!',
                    dest=language_code)
            else:
                # Get channel details using the Telegram API
                channel = await bot.get_chat(chat_id=ch_user_id100)

                if check[3] == user_id or user_id == ADMIN:
                    # Delete the channel if the user is authorized
                    db.delete_channel(channel_id=ch_user_id)
                    tx = translator(text='<b><i>🚫 Channel removed...</i></b>\n', dest=language_code)
                    text = (f"{tx}\n"
                            f"<b>Name:</b> <i>{channel.full_name}</i>\n"
                            f"<b>Username:</b> <i>@{channel.username}</i>\n"
                            f"<b>ID:</b> <i><code>{ch_user_id}</code></i>\n\n")
                else:
                    # Inform the user if they do not have permission to delete the channel
                    text = translator(text='⭕ Only an admin can delete this channel.', dest=language_code)
        else:
            # Inform the user if they lack the necessary permissions
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)

        await bot.edit_message_text(chat_id=user_id,
                                    message_id=mid,
                                    text=f'{text}',
                                    reply_markup=btn)  # Send or edit the message with the result
        await state.update_data({
            "message_id": call.message.message_id
        })  # Update the FSM state with the current message ID
    except Exception as err:
        logging.error(err)  # Log any errors that occur during the process
