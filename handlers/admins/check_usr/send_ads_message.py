import logging
from loader import dp, bot
from aiogram import types
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState

@dp.message(AdminState.send_message_to_user, IsAdmin())
async def send_ads_message(msg: types.Message, state: FSMContext):
    """
    Handles sending a message from an admin to a specific user in a Telegram bot.

    Parameters:
    - msg (types.Message): The message object containing the content to be sent.
    - state (FSMContext): Finite State Machine context used to manage the current state of the admin.

    Functionality:
    - Retrieves the admin's ID, language code, and message data from the state.
    - Checks if the admin has the permission to send messages using the `SelectAdmin` filter.
    - If authorized, forwards the message content to the target user.
    - Sends a confirmation message to the admin indicating success or an error message if something goes wrong.
    - Clears the state data after the operation is complete.
    - Logs any exceptions that occur during execution.

    Returns:
    - This function is asynchronous and does not return a value but performs actions such as sending messages and updating states.
    """
    try:
        user_id = msg.from_user.id  # The ID of the admin sending the message
        language = msg.from_user.language_code  # The language code of the admin for message translation
        data_state = await state.get_data()  # Retrieve data from the FSM context
        target_user_id = data_state['user_id']  # The ID of the target user who will receive the message
        is_admin = SelectAdmin(cid=user_id)  # Check if the admin is authorized to send messages
        button = close_btn()  # Inline button to close the message

        if is_admin.send_message():
            try:
                # Forward the message content to the target user
                await bot.copy_message(
                    chat_id=target_user_id,
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,  # Include the original caption if available
                    reply_markup=msg.reply_markup  # Include the original reply markup if available
                )
                text = translator(
                    text='✅ Message sent',
                    dest=language
                )
            except Exception as err:
                # Handle any errors that occur during the message forwarding
                text = translator(
                    text='Something went wrong. ERROR:',
                    dest=language
                ) + str(err)
                await state.clear()  # Clear the state if an error occurs
                logging.error(err)  # Log the error details
        else:
            # Inform the admin that they do not have the necessary permissions
            text = translator(
                text='❌ Unfortunately, you do not have this permission!',
                dest=language
            )
            await state.clear()  # Clear the state if the admin lacks permission

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=data_state['message_id'],
            text=f'<b><i>{text}</i></b>',
            reply_markup=button  # Update the message with a translated response
        )
        await state.clear()  # Clear the FSM state after the operation
        await state.update_data({"message_id": msg.message_id})  # Update the state with the new message ID

    except Exception as err:
        logging.error(err)  # Log any exceptions that occur

