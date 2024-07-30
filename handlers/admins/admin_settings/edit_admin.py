import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from data.config import ADMIN
from filters.admin import IsAdmin, SelectAdmin
from function.function import x_or_y
from function.translator import translator
from keyboards.inline.close_btn import close_btn
from loader import dp, bot, db
from states.admin_state import AdminState
from keyboards.inline.button import EditAdminSetting
from keyboards.inline.admin_btn import attach_admin_btn


@dp.callback_query(EditAdminSetting.filter(F.action == "edit"), IsAdmin())
async def edit_admin(call: types.CallbackQuery, callback_data: EditAdminSetting, state: FSMContext):
    """
    Handles the callback query for editing admin settings.

    Parameters:
    - call (types.CallbackQuery): The callback query object triggered by the admin's action.
    - callback_data (EditAdminSetting): Data extracted from the callback query, including the admin ID and the edit key.
    - state (FSMContext): The FSM context for managing the bot's conversation state.

    Functionality:
    - Extracts the current admin's ID (`cid`), message ID (`mid`), language code (`lang`), target admin ID (`admin_cid`), and the key to be edited (`edit_key`).
    - Checks if the current admin has the right to modify admin settings.
    - If permitted, fetches the target admin's data.
    - Depending on the edit key, either deletes the target admin or updates a specific admin permission.
    - Constructs a response message detailing the updated admin rights.
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
        admin_cid = callback_data.cid  # ID of the target admin to be modified
        edit_key = callback_data.data  # The key indicating what action to perform
        data = SelectAdmin(cid=cid)  # Fetches the current admin's data
        add_admin = data.add_admin()  # Checks if the current admin can add admins
        btn = close_btn()  # Default button to close the operation

        # Check if the admin has rights to add another admin
        if add_admin:
            admin_data = db.select_admin(cid=admin_cid)  # Fetch data for the target admin
            if admin_data is None:
                text = f'⛔{admin_cid} {translator(text="😪 Not available in admin list!", dest=lang)}'
            else:
                if admin_data[2] == cid or cid == ADMIN:
                    if edit_key == "delete_admin":
                        # If the edit action is to delete the admin
                        db.delete_admin(cid=admin_cid)
                        admin_info = await bot.get_chat(chat_id=admin_cid)
                        text = f'🔪 @{admin_info.username} {translator(text="✅ Removed from admin!", dest=lang)}'
                        await bot.send_message(chat_id=admin_cid, text='😪 Your admin rights have been revoked!')
                    else:
                        # Update the specific admin permission
                        select_column = db.select_admin_column(cid=admin_cid, column=edit_key)
                        new_value = 0 if select_column[0] == 1 else 1
                        db.update_admin_data(cid=admin_cid, column=edit_key, value=new_value)
                        btn = attach_admin_btn(cid=admin_cid, lang=lang)
                        is_admin = SelectAdmin(cid=admin_cid)
                        send_message_tx = x_or_y(is_admin.send_message())
                        view_statistika_tx = x_or_y(is_admin.view_statistika())
                        download_statistika_tx = x_or_y(is_admin.download_statistika())
                        block_user_tx = x_or_y(is_admin.block_user())
                        channel_settings_tx = x_or_y(is_admin.channel_settings())
                        add_admin_tx = x_or_y(is_admin.add_admin())
                        text = f'<b>👮 Change saved!</b>\n\n' \
                               f'<b>Send message: {send_message_tx}</b>\n' \
                               f'<b>View statistics: {view_statistika_tx}</b>\n' \
                               f'<b>Download statistics: {download_statistika_tx}</b>\n' \
                               f'<b>Block user: {block_user_tx}</b>\n' \
                               f'<b>Channel settings: {channel_settings_tx}</b>\n' \
                               f'<b>Add admin: {add_admin_tx}</b>\n' \
                               f'<b>Date added: </b>'
                        text += str(admin_data[9])
                else:
                    text = translator(text='🛑 You can only change the admin rights you assigned!', dest=lang)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=lang)

        # Update the message with the admin rights information or error message
        await bot.edit_message_text(chat_id=cid, message_id=mid, text=f"<b>{text}</b>", reply_markup=btn)
        await state.set_state(AdminState.add_admin)  # Set the state to add admin
        await state.update_data({"message_id": call.message.message_id})  # Update the state data with the message ID
    except Exception as err:
        logging.error(err)  # Log any errors that occur

