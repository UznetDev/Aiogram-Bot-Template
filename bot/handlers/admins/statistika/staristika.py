from aiogram import F
from aiogram import types
from aiogram.fsm.context import FSMContext


from bot.filters.admin import IsAdmin
from bot.data.config import yil_oy_kun, soat_minut_sekund
from bot.keyboards.inline.close_btn import close_btn
from bot.keyboards.inline.button import AdminCallback
from bot.keyboards.inline.admin_btn import download_statistika
from bot.loader import dp, db, translator, AM, root_logger


@dp.callback_query(AdminCallback.filter(F.action == "view_statistika"), IsAdmin())
async def statistika(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id
        message_id = call.message.message_id
        language = call.from_user.language_code

        if AM(user_id=user_id, feature='view_statistika'):
            user_count = db.stat()
            ban_count = db.stat_ban()
            text = (translator(text="👥 Bot users count: ", dest=language) + str(user_count) +
                    ' .\n' + translator(text="⏰ Time:", dest=language) +
                    f" {soat_minut_sekund}\n" + translator(text="📆 Date:", dest=language) +
                    f' {yil_oy_kun}\n ' + translator(text="Number of bans: ", dest=language) + str(
                        ban_count))
            button = download_statistika(user_id=user_id, language_code=language)
            await state.update_data({"message_id": call.message.message_id})
        else:
            text = translator(text="❌ Unfortunately, you do not have this permission!", dest=language)
            button = close_btn()

        await call.message.edit_text(text=f'<b><i>{text}</i></b>', reply_markup=button)
        await state.update_data({"message_id": message_id})

    except Exception as err:
        root_logger.error(err)

