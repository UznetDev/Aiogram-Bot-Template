import logging
from loader import dp, db
from aiogram import types
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from keyboards.inline.admin_btn import download_statistika
from aiogram import F
from aiogram.fsm.context import FSMContext
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from data.config import yil_oy_kun, soat_minut_sekund


@dp.callback_query(AdminCallback.filter(F.action == "statistika"), IsAdmin())
async def statistika(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the callback query for retrieving and displaying bot statistics to an admin.

    This function:
    - Checks if the user has the permission to view statistics.
    - Retrieves and formats bot user count, ban count, and current date/time.
    - Updates the message with statistics or a permission error message.
    - Updates the FSM context with the new message ID and manages the reply markup.

    Args:
        call (types.CallbackQuery): The callback query object containing the data and user information.
        state (FSMContext): The finite state machine context for managing state data.

    Raises:
        Exception: Logs any errors encountered during the process.

    Returns:
        None
    """
    try:
        user_id = call.from_user.id
        message_id = call.message.message_id
        language = call.from_user.language_code
        is_admin = SelectAdmin(cid=user_id)

        if is_admin.view_statistika():
            user_count = db.stat()
            ban_count = db.stat_ban()
            text = (translator(text="👥 Bot users count: ", dest=language) + str(user_count) +
                    ' .\n' + translator(text="⏰ Time:", dest=language) +
                    f" {soat_minut_sekund}\n" + translator(text="📆 Date:", dest=language) +
                    f' {yil_oy_kun}\n ' + translator(text="Number of bans: ", dest=language) + str(
                        ban_count))
            button = download_statistika(cid=user_id, lang=language)
            await state.update_data({"message_id": call.message.message_id})
        else:
            text = translator(text="❌ Unfortunately, you do not have this permission!", dest=language)
            button = close_btn()

        await call.message.edit_text(text=f'<b><i>{text}</i></b>', reply_markup=button)
        await state.update_data({"message_id": message_id})

    except Exception as err:
        logging.error(err)

