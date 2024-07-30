import logging
from loader import dp, bot
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState

@dp.callback_query(AdminCallback.filter(F.action == "check_user"), IsAdmin())
async def check_user(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the process of checking a user's details by an admin in a Telegram bot.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing details about the callback.
    - state (FSMContext): Finite State Machine context used to manage user states.

    Functionality:
    - Retrieves the admin's ID and message details from the callback query.
    - Uses the admin's ID to verify if they have the necessary permissions to check a user's details.
    - If the admin is authorized, prompts them to send the user ID they want to check.
    - If not authorized, sends a message indicating that the admin lacks the required permissions.
    - Updates the admin's state to `AdminState.check_user` and the state data with the message ID.
    - Edits the original message with the result of the check.
    - Logs any exceptions that occur during execution.

    Returns:
    - This function is asynchronous and does not return a value but performs actions such as sending messages and updating states.
    """
    try:
        user_id = call.from_user.id  # The ID of the admin initiating the check
        message_id = call.message.message_id  # The ID of the message triggering the callback
        language = call.from_user.language_code  # The language code of the admin for message translation
        data = SelectAdmin(cid=user_id)  # Check if the admin is authorized to perform the action
        button = close_btn()  # Inline button to close the message

        if data.block_user():
            # If the admin is authorized, prompt for the user ID to check
            text = translator(
                text='🔰Please send the user ID you want to check...',
                dest=language
            )
            await state.set_state(AdminState.check_user)  # Update the FSM state
        else:
            # If the admin is not authorized, inform them of the lack of permissions
            text = translator(
                text='❌ Unfortunately, you do not have the required permissions!',
                dest=language
            )

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=message_id,
            text=f'<b><i>{text}</i></b>',
            reply_markup=button  # Update the message with a translated response
        )

        await state.update_data({"message_id": call.message.message_id})  # Save the message ID in the FSM context
    except Exception as err:
        logging.error(err)  # Log any exceptions that occur
