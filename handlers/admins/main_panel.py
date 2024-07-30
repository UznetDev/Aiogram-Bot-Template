import logging
from loader import dp, bot
from aiogram.filters import Command
from aiogram import types
from keyboards.inline.admin_btn import main_admin_panel_btn
from filters.admin import IsAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator


@dp.message(Command(commands='admin'), IsAdmin())
async def main_panel(msg: types.Message, state: FSMContext):
    """
    Handles the '/admin' command for admin users. Sends a welcome message with an admin panel inline keyboard.

    - Retrieves the user ID and message ID from the incoming message.
    - Translates and sends a welcome message to the user with an inline keyboard.
    - Deletes any previous message stored in the state to avoid clutter.
    - Updates the state with the new message ID.
    - Deletes the original command message to keep the chat clean.

    Args:
        msg (types.Message): The incoming message object.
        state (FSMContext): The finite state machine context to manage state data.

    Raises:
        Exception: Logs any errors encountered during the process.
    """
    try:
        cid = msg.from_user.id
        mid = msg.message_id
        lang = msg.from_user.language_code

        # Translate and send the welcome message with admin panel buttons
        welcome_text = translator(text=f'👩‍💻Hello, dear admin, welcome to the main panel!',
                                  dest=lang)
        response_msg = await msg.answer(text=f'<b>{welcome_text}</b>',
                                        reply_markup=main_admin_panel_btn(cid=cid, lang=lang))

        # Manage previous message
        state_data = await state.get_data()
        try:
            if 'message_id' in state_data and state_data['message_id'] > 1:
                await bot.delete_message(chat_id=cid, message_id=state_data['message_id'])
        except Exception as err:
            logging.error(f"Error deleting previous message: {err}")

        # Update the state with the new message ID
        await state.update_data({
            "message_id": response_msg.message_id
        })

        # Delete the original command message
        await bot.delete_message(chat_id=cid, message_id=mid)

    except Exception as err:
        logging.error(f"Unhandled error: {err}")

