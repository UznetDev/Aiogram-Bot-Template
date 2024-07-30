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
async def attach_admins(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        admin_cid = call.data.split(':')[2]
        data = SelectAdmin(cid=cid)
        btn = close_btn()
        if data.add_admin():
            admin_data = db.select_admin(cid=admin_cid)
            if admin_data[2] == cid or cid == ADMIN:
                btn = attach_admin_btn(cid=admin_cid, lang=lang)
                is_admin = SelectAdmin(cid=admin_cid)
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
                text = translator(text=text, dest=lang) + str(admin_data[9])
            else:
                text = translator(text='<b>😪You can only change the admin rights you added!</b>', dest=lang)
        else:
            text = translator(text='<b>❌ Unfortunately, you do not have this right!</b>', dest=lang)
        await bot.edit_message_text(chat_id=cid, message_id=mid, text=text, reply_markup=btn)
        await state.set_state(AdminState.add_admin)
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        logging.error(err)
