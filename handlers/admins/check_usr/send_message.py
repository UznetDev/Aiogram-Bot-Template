import logging
from loader import dp, bot
from aiogram import types, F
from keyboards.inline.button import BlockUser
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState

@dp.callback_query(IsAdmin(), BlockUser.filter(F.action == "send_message"))
async def send_message(call: types.CallbackQuery, callback_data: BlockUser, state: FSMContext):
    """
    Initiates the process for an admin to send a message to a specific user in a Telegram bot.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing details about the callback.
    - callback_data (BlockUser): Custom data extracted from the callback query, including the target user ID.
    - state (FSMContext): Finite State Machine context used to manage user states.

    Functionality:
    - Extracts the target user ID, admin's ID, message ID, and language code from the callback data and query.
    - Verifies if the admin has the permission to send messages using the `SelectAdmin` filter.
    - If authorized, prompts the admin to send the message content they want to deliver to the target user.
    - If not authorized, sends a message indicating that the admin lacks the necessary permissions.
    - Updates the admin's state to `AdminState.send_message_to_user` and the state data with relevant information.
    - Edits the original message with the result of the permission check and prompt for message content.
    - Logs any exceptions that occur during execution.

    Returns:
    - This function is asynchronous and does not return a value but performs actions such as sending messages and updating states.
    """
    try:
        target_user_id = callback_data.cid  # The ID of the user to whom the message will be sent
        user_id = call.from_user.id  # The ID of the admin initiating the message send action
        message_id = call.message.message_id  # The ID of the message triggering the callback
        language = call.from_user.language_code  # The language code of the admin for message translation
        admin_check = SelectAdmin(cid=user_id)  # Check if the admin has permission to send messages
        button = close_btn()  # Inline button to close the message

        if admin_check.send_message():
            # Prompt the admin to send the message content for the user
            text = translator(
                text="🗨 Send me the message for the user...",
                dest=language
            )
            await state.set_state(AdminState.send_message_to_user)  # Set the FSM state for sending a message
        else:
            # Inform the admin that they do not have the necessary permissions
            text = translator(
                text="❌ Unfortunately, you do not have this permission!",
                dest=language
            )

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=message_id,
            text=f'<b><i>{text}</i></b>',
            reply_markup=button  # Update the message with a translated response
        )

        await state.update_data({
            "message_id": call.message.message_id,  # Save the message ID in the FSM context
            "user_id": target_user_id  # Save the target user ID in the FSM context
        })
    except Exception as err:
        logging.error(err)  # Log any exceptions that occur

