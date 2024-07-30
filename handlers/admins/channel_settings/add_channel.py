import logging
from loader import dp, bot
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState

@dp.callback_query(AdminCallback.filter(F.action == "add_channel"), IsAdmin())
async def add_channel(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the process of adding a channel by an admin in a Telegram bot.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing details about the callback.
    - state (FSMContext): Finite State Machine context used to manage the current state of the admin.

    Functionality:
    - Retrieves the admin's ID, message ID, and language code from the callback query.
    - Checks if the admin has the necessary permissions to add a channel using the `SelectAdmin` filter.
    - If authorized, prompts the admin to send the channel ID and updates the admin's state to `AdminState.add_channel`.
    - If not authorized, sends a message indicating that the admin lacks the necessary permissions.
    - Edits the original message with the result of the permission check and the prompt for the channel ID.
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
            # If the admin is authorized, prompt for the channel ID
            await state.set_state(AdminState.add_channel)  # Set the FSM state for adding a channel
            text = translator(text="😊 Please send the channel id...", dest=lang)
            await state.update_data({"message_id": call.message.message_id})  # Save the message ID in the FSM context
        else:
            # Inform the admin that they do not have the necessary permissions
            text = translator(text="❌ Unfortunately, you do not have this right!", dest=lang)

        await bot.edit_message_text(
            chat_id=cid,
            message_id=mid,
            text=f'{text}',
            reply_markup=btn  # Update the message with a translated response
        )
        await state.update_data({"message_id": call.message.message_id})  # Save the message ID in the FSM context
    except Exception as err:
        logging.error(err)  # Log any exceptions that occur
