import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.admin_btn import channel_settings
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator


@dp.callback_query(AdminCallback.filter(F.action == "mandatory_membership"), IsAdmin())
async def mandatory_membership(call: types.CallbackQuery, state: FSMContext):
    """
    Toggles the mandatory membership setting for a channel and updates the bot's response message.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing the information from the user's action.
    - state (FSMContext): The FSM context to manage the bot's state during the conversation.

    Functionality:
    - Retrieves the admin's user ID (`user_id`), the message ID (`mid`), and the language_codeuage code (`language_code`) from the callback query.
    - Checks if the user has the required permissions to modify channel settings using the `SelectAdmin` filter.
    - If authorized, reads the current mandatory membership status from the database.
    - Toggles the membership requirement status:
        - If currently enabled, disables it and updates the database.
        - If currently disabled, enables it and updates the database.
    - Updates the message in the chat with the new status and a close button (`close_btn`).
    - If the user does not have the required permissions, informs them with an appropriate message.
    - Updates the state with the message ID to reflect the latest changes.

    Returns:
    - This function is asynchronous and does not return a value. It interacts with the Telegram API to update messages and with the database to modify settings.
    """
    try:
        user_id = call.from_user.id  # The ID of the admin who initiated the action
        mid = call.message.message_id  # The ID of the message to be updated
        language_code = call.from_user.language_code  # The language_codeuage code for translation
        data = SelectAdmin(user_id=user_id)  # Check if the user has admin permissions
        btn = close_btn()  # Create a button for closing the message

        if data.channel_settings():
            # Read the current setting for mandatory membership from the database
            mandatory_membership = db.select_setting('mandatory_membership')
            if mandatory_membership == 'True':
                # If mandatory membership is enabled, disable it
                text = translator(text='☑️ Forced membership disabled!', dest=language_code)
                nex_mandatory_membership = 'False'
            else:
                # If mandatory membership is disabled, enable it
                text = translator(text='✅ Mandatory membership enabled!', dest=language_code)
                nex_mandatory_membership = 'True'

            # Update the database with the new membership status
            db.update_settings_key(updater_user_id=user_id, key='mandatory_membership', value=nex_mandatory_membership)
            btn = channel_settings(language_code=language_code)  # Update the button to reflect the new settings
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)

        # Edit the message with the new status and close button
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=mid,
                                    text=f'<b><i>{text}</i></b>',
                                    reply_markup=btn)
        # Update FSM state with the current message ID
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        # Log any errors that occur during the execution
        logging.error(err)
