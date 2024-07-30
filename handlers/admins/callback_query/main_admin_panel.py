import logging
from loader import dp, bot
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.admin_btn import main_admin_panel_btn
from filters.admin import IsAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator


@dp.callback_query(AdminCallback.filter(F.action == "main_adm_panel"), IsAdmin())
async def main_panel(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the callback query for navigating to the main admin panel.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing information about the user's action.
    - state (FSMContext): The FSM context to manage the bot's state during the conversation.

    Functionality:
    - Retrieves the admin's user ID (`cid`), the message ID (`mid`), and the language code (`lang`) from the callback query.
    - Translates a greeting message to the admin in their preferred language.
    - Edits the original message in the chat to display the translated greeting and the main admin panel buttons.
    - Updates the FSM state with the current message ID.

    Returns:
    - This function is asynchronous and does not return a value. It interacts with the Telegram API to update messages and manage the state.

    Error Handling:
    - Catches and logs any exceptions that occur during the execution, ensuring that errors are recorded for debugging.
    """
    try:
        cid = call.from_user.id  # The ID of the admin who initiated the action
        mid = call.message.message_id  # The ID of the message to be updated
        lang = call.from_user.language_code  # The language code for translation

        # Translate the greeting message
        text = translator(text="👩‍💻Hello, dear admin, welcome to the main panel!", dest=lang)

        # Edit the message with the translated text and update it with the main admin panel buttons
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f'{text}',
                                    reply_markup=main_admin_panel_btn(cid=cid, lang=lang))

        # Update FSM state with the current message ID
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        # Log any errors that occur during execution
        logging.error(err)

