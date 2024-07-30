import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from filters.admin import IsAdmin, SelectAdmin
from function.translator import translator
from keyboards.inline.admin_btn import admin_setting
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from loader import dp, bot

@dp.callback_query(AdminCallback.filter(F.action == "admin_settings"), IsAdmin())
async def admin_settings(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the callback query for accessing the Admin settings.

    Parameters:
    - call (types.CallbackQuery): The callback query object from the admin's interaction.
    - state (FSMContext): The FSM context to manage the bot's state during the conversation.

    Functionality:
    - Retrieves the ID of the admin (`cid`), the message ID (`mid`), and the language code (`lang`).
    - Checks if the admin has the permissions to access the Admin settings.
    - If permissions are granted, presents the admin with the settings options.
    - If permissions are denied, informs the admin that they lack the necessary rights.
    - Updates the original message with the appropriate response and buttons.

    Returns:
    - This function is asynchronous and does not return a value. It interacts with the Telegram API to update messages.

    Error Handling:
    - Catches and logs any exceptions that occur during the process of handling the callback query or updating the message.
    """
    try:
        cid = call.from_user.id  # ID of the admin initiating the request
        mid = call.message.message_id  # ID of the message to be updated
        lang = call.from_user.language_code  # Language code for translation
        data = SelectAdmin(cid=cid)  # Retrieves admin settings for the current user
        add_admin = data.add_admin()  # Checks if the user has the right to access admin settings

        if add_admin:
            # The admin has the right to access settings
            text = translator(text="❗ You are in the Admin settings section!", dest=lang)
            btn = await admin_setting(cid=cid, lang=lang)  # Prepare admin settings buttons
        else:
            # The admin does not have the necessary rights
            text = translator(text="❌ Unfortunately, you do not have this right!", dest=lang)
            btn = close_btn()  # Prepare close button

        # Update the message with the appropriate response and buttons
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f'<b>{text}</b>',
                                    reply_markup=btn)
        # Update the state data with the current message ID
        await state.update_data({"message_id": mid})
    except Exception as err:
        logging.error(err)  # Log any errors that occur

