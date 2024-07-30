import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from data.config import ADMIN

@dp.callback_query(IsAdmin(), AdminCallback.filter(F.action == "delete_channel"))
async def delete_channel(call: types.CallbackQuery, callback_data: AdminCallback, state: FSMContext):
    """
    Handles the deletion of a channel in a Telegram bot by an authorized admin.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing details about the interaction.
    - callback_data (AdminCallback): Contains the action and additional data, including the channel ID.
    - state (FSMContext): FSM context used to manage the bot's state for the current conversation.

    Functionality:
    - Retrieves the admin's user ID (`cid`), the message ID (`mid`), and the language code (`lang`) from the callback query.
    - Checks if the user has the necessary permissions to manage channel settings using the `SelectAdmin` filter.
    - If authorized, retrieves the channel ID from `callback_data`, formats it, and checks its existence in the database.
    - If the channel exists and the user is authorized, deletes the channel from the database and notifies the user.
    - If the channel does not exist or the user is not authorized, sends an appropriate message to the user.
    - Updates the bot message with the result of the operation and a close button (`close_btn`).
    - Catches and logs any exceptions that occur during the execution.

    Returns:
    - This function is asynchronous and does not return a value. It interacts with the Telegram API to send and edit messages.
    """
    try:
        cid = call.from_user.id  # The ID of the admin making the request
        mid = call.message.message_id  # The ID of the message associated with the callback
        lang = call.from_user.language_code  # The language code for translating responses
        data = SelectAdmin(cid=cid)  # Check if the user has admin permissions
        btn = close_btn()  # A button for closing the message

        if data.channel_settings():
            ch_cid = callback_data.data  # Channel ID from the callback data
            ch_cid100 = str(-100) + str(ch_cid)  # Format channel ID for API
            check = db.check_channel(cid=ch_cid)  # Check if the channel exists in the database

            if not check:
                # Inform the user if the channel does not exist
                text = translator(
                    text='⭕ Channel not found!\nThe channel seems to have been deleted previously!',
                    dest=lang)
            else:
                # Get channel details using the Telegram API
                channel = await bot.get_chat(chat_id=ch_cid100)

                if check[3] == cid or cid == ADMIN:
                    # Delete the channel if the user is authorized
                    db.delete_channel(cid=ch_cid)
                    tx = translator(text='<b><i>🚫 Channel removed...</i></b>\n', dest=lang)
                    text = (f"{tx}\n"
                            f"<b>Name:</b> <i>{channel.full_name}</i>\n"
                            f"<b>Username:</b> <i>@{channel.username}</i>\n"
                            f"<b>ID:</b> <i><code>{ch_cid}</code></i>\n\n")
                else:
                    # Inform the user if they do not have permission to delete the channel
                    text = translator(text='⭕ Only an admin can delete this channel.', dest=lang)
        else:
            # Inform the user if they lack the necessary permissions
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=lang)

        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f'{text}',
                                    reply_markup=btn)  # Send or edit the message with the result
        await state.update_data({
            "message_id": call.message.message_id
        })  # Update the FSM state with the current message ID
    except Exception as err:
        logging.error(err)  # Log any errors that occur during the process
