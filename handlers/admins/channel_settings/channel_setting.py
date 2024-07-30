import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.admin_btn import channel_settings
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from data.config import ADMIN


@dp.callback_query(AdminCallback.filter(F.action == "channel_setting"), IsAdmin())
async def channel_setting(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the display of channel settings for an admin in a Telegram bot.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing details about the callback.
    - state (FSMContext): Finite State Machine context used to manage the current state of the admin.

    Functionality:
    - Extracts the admin's ID, message ID, and language code from the callback query.
    - Verifies if the admin has the necessary permissions to manage channel settings using the `SelectAdmin` filter.
    - If the admin is the main ADMIN, retrieves all channels from the database; otherwise, retrieves channels added by the admin.
    - Constructs a message displaying the list of channels, including details such as the channel's name, username, added date, and the admin who added it.
    - If no channels are found, sends a message indicating the list is empty.
    - Updates the message with channel settings and appropriate buttons.
    - Logs any exceptions that occur during execution.

    Returns:
    - This function is asynchronous and does not return a value but performs actions such as sending messages and updating states.
    """
    try:
        cid = call.from_user.id  # The ID of the admin initiating the action
        mid = call.message.message_id  # The ID of the message triggering the callback
        lang = call.from_user.language_code  # The language code of the admin for message translation
        data = SelectAdmin(cid=cid)  # Check if the admin has permission to manage channel settings
        btn = close_btn()  # Inline button to close the message

        if data.channel_settings():
            if cid == ADMIN:
                # Retrieve all channels if the admin is the main ADMIN
                data = db.select_channels()
            else:
                # Retrieve channels added by the current admin
                data = db.select_channels_add_cid(add_cid=cid)

            if not data:
                # If no channels are found, indicate that the list is empty
                text = translator(text="❔ The channel list is empty!\n\n", dest=lang)
            else:
                # Construct a message listing the channels
                text = translator(text="🔰 List of channels:\n\n", dest=lang)
                count = 0
                for x in data:
                    try:
                        count += 1
                        chat_id = str(-100) + str(x[1])  # Telegram channel ID
                        channel = await bot.get_chat(chat_id=chat_id)  # Get channel details
                        text += (f"<b><i>{count}</i>. Name:</b> <i>{channel.full_name}</i>\n"
                                 f"<b>Username:</b> <i>@{channel.username}\n</i>"
                                 f"<b>Added date:</b> <i>{x[2]}\n</i>"
                                 f"<b>Added by CID:</b> <i>{x[3]}\n\n</i>")
                    except Exception as err:
                        logging.error(err)  # Log any errors in retrieving channel details
            btn = channel_settings(lang=lang)  # Button for channel settings
        else:
            # Inform the admin that they do not have the necessary permissions
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=lang)

        await bot.edit_message_text(
            chat_id=cid,
            message_id=mid,
            text=f'<b><i>{text}</i></b>',
            reply_markup=btn  # Update the message with a translated response and appropriate buttons
        )

        await state.update_data({"message_id": call.message.message_id})  # Save the message ID in the FSM context
    except Exception as err:
        logging.error(err)  # Log any exceptions that occur

