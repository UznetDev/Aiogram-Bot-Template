import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from data.config import ADMIN
from filters.admin import IsAdmin, SelectAdmin
from function.function import x_or_y
from function.translator import translator
from keyboards.inline.admin_btn import attach_admin_btn
from keyboards.inline.button import AdminSetting
from keyboards.inline.close_btn import close_btn
from loader import dp, bot, db
from states.admin_state import AdminState


@dp.callback_query(AdminSetting.filter(F.action == "attach_admin"), IsAdmin())
async def attach_admins(call: types.CallbackQuery, callback_data: AdminSetting, state: FSMContext):
    """
    Handles the callback query for attaching admin rights to a user.

    Parameters:
    - call (types.CallbackQuery): The callback query object triggered by the admin's action.
    - callback_data (AdminSetting): Data extracted from the callback query, including the admin ID.
    - state (FSMContext): The FSM context for managing the bot's conversation state.

    Functionality:
    - Extracts the admin's ID (`cid`), message ID (`mid`), language code (`lang`), and the target admin ID (`admin_cid`).
    - Checks if the current admin has the right to modify admin settings.
    - If permitted, fetches the target admin's data and checks the permissions of the current admin.
    - Constructs a response message detailing the target admin's rights.
    - Updates the message with the constructed text and appropriate buttons.
    - Sets the FSM state to `AdminState.add_admin`.

    Returns:
    - This function is asynchronous and interacts with the Telegram API to update messages.

    Error Handling:
    - Catches and logs any exceptions that occur during the execution of the function.
    """
    try:
        cid = call.from_user.id  # Current admin's ID
        mid = call.message.message_id  # Message ID to be updated
        lang = call.from_user.language_code  # Admin's language preference
        admin_cid = callback_data.cid  # ID of the admin to be modified
        data = SelectAdmin(cid=cid)  # Fetches the current admin's data
        btn = close_btn()  # Default button to close the operation

        # Check if the admin has rights to add another admin
        if data.add_admin():
            admin_data = db.select_admin(cid=admin_cid)  # Fetch data for the target admin
            if admin_data[2] == cid or cid == ADMIN:
                # If the current admin added the target admin or is the primary admin
                btn = attach_admin_btn(cid=admin_cid, lang=lang)  # Buttons for setting admin rights
                is_admin = SelectAdmin(cid=admin_cid)  # Check target admin's permissions

                # Format the text showing current permissions of the target admin
                send_message_tx = x_or_y(is_admin.send_message())
                view_statistika_tx = x_or_y(is_admin.view_statistika())
                download_statistika_tx = x_or_y(is_admin.download_statistika())
                block_user_tx = x_or_y(is_admin.block_user())
                channel_settings_tx = x_or_y(is_admin.channel_settings())
                add_admin_tx = x_or_y(is_admin.add_admin())

                text = f'<b>👮‍♂️Admin rights!</b>\n\n' \
                       f'<b>Send message: {send_message_tx}</b>\n' \
                       f'<b>View statistics: {view_statistika_tx}</b>\n' \
                       f'<b>Download statistics: {download_statistika_tx}</b>\n' \
                       f'<b>Block user: {block_user_tx}</b>\n' \
                       f'<b>Channel settings: {channel_settings_tx}</b>\n' \
                       f'<b>Add admin: {add_admin_tx}</b>\n' \
                       f'<b>Date added: </b>'
            else:
                # If the current admin does not have the right to modify the target admin
                text = translator(text='😪You can only change the admin rights you added!', dest=lang)
        else:
            # If the current admin does not have the necessary rights
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=lang)

        # Update the message with the admin rights information or error message
        await bot.edit_message_text(chat_id=cid, message_id=mid, text=f'{text}', reply_markup=btn)
        await state.set_state(AdminState.add_admin)  # Set the state to add admin
        await state.update_data({"message_id": call.message.message_id})  # Update the state data with the message ID
    except Exception as err:
        logging.error(err)  # Log any errors that occur
