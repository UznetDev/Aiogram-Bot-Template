import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from filters.admin import IsAdmin, SelectAdmin
from function.translator import translator
from keyboards.inline.admin_btn import admin_setting
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from loader import dp, bot
from states.admin_state import AdminState

@dp.callback_query(AdminCallback.filter(F.action == "add_admin"), IsAdmin())
async def add_admin_first(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the initial request to add a new admin.

    Parameters:
    - call (types.CallbackQuery): The callback query object from the admin's interaction.
    - state (FSMContext): The FSM context to manage the bot's state during the conversation.

    Functionality:
    - Retrieves the ID of the admin who initiated the request (`cid`), the message ID (`mid`), and the language code (`lang`).
    - Checks if the requesting admin has the rights to add a new admin.
    - If the requesting admin has the necessary permissions, prompts them to send the ID of the new admin to be added.
    - Sets the state to `AdminState.add_admin` to handle the next step of the process.
    - If the requesting admin does not have the necessary permissions, sends a message indicating lack of rights.
    - Updates the original message with the appropriate response and buttons based on the outcome.

    Returns:
    - This function is asynchronous and does not return a value. It interacts with the Telegram API to update messages and manage the state.

    Error Handling:
    - Catches and logs any exceptions that occur during the process of handling the callback query or updating the message.
    """
    try:
        cid = call.from_user.id  # ID of the admin initiating the request
        mid = call.message.message_id  # ID of the message to be updated
        lang = call.from_user.language_code  # Language code for translation
        data = SelectAdmin(cid=cid)  # Retrieves admin settings for the current user
        add_admin = data.add_admin()  # Checks if the user has the right to add an admin

        if add_admin:
            # Prompt the user to provide the ID of the new admin
            text = translator(text="🔰 Please send the admin ID number you want to add...", dest=lang)
            btn = await admin_setting(cid=cid, lang=lang)  # Prepare admin settings buttons
            await state.set_state(AdminState.add_admin)  # Set the FSM state for adding an admin
        else:
            # Inform the user that they do not have the necessary permissions
            text = translator(text="❌ Unfortunately, you do not have this right!", dest=lang)
            btn = close_btn()  # Prepare close button

        # Update the message with the appropriate response and buttons
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f'<b>{text}</b>',
                                    reply_markup=btn)
        # Update the state data with the current message ID
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        logging.error(err)  # Log any errors that occur

