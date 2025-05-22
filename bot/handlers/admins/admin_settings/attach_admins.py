from aiogram import types, F
from aiogram.fsm.context import FSMContext

from bot.data.config import ADMIN
from bot.filters.admin import IsAdmin, AdminFilter
from bot.function.function import x_or_y
from bot.keyboards.inline.admin_btn import attach_admin_btn
from bot.keyboards.inline.button import AdminSetting
from bot.keyboards.inline.close_btn import close_btn
from bot.loader import dp, bot, db, root_logger, translator
from bot.states.admin_state import AdminState



@dp.callback_query(AdminSetting.filter(F.action == "attach_admin"), IsAdmin())
async def attach_admins(call: types.CallbackQuery, callback_data: AdminSetting, state: FSMContext):

    try:
        user_id = call.from_user.id
        mid = call.message.message_id
        language_code = call.from_user.language_code
        admin_user_id = callback_data.user_id
        data = AdminFilter(user_id=user_id)
        btn = close_btn()

        if data.add_admin():
            admin_data = db.select_admin(user_id=admin_user_id)
            if admin_data['initiator_user_id'] == user_id or user_id == ADMIN:
                btn = attach_admin_btn(user_id=admin_user_id, 
                                       language_code=language_code)
                is_admin = AdminFilter(user_id=admin_user_id)


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
                text = translator(text='😪You can only change the admin rights you added!', dest=language_code)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)

        await bot.edit_message_text(chat_id=user_id, message_id=mid, text=f'{text}', reply_markup=btn)
        await state.set_state(AdminState.add_admin)
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        root_logger.error(err)
