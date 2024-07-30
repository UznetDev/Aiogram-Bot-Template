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
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        admin_cid = callback_data.cid
        edit_key = callback_data.data
        data = SelectAdmin(cid=cid)
        add_admin = data.add_admin()
        btn = close_btn()
        if add_admin:
            admin_data = db.select_admin(cid=admin_cid)
            if admin_data is None:
                text = f'⛔{admin_cid} {translator(text="😪 Not available in admin list!", dest=lang)}'
            else:
                if admin_data[2] == cid or cid == ADMIN:
                    if edit_key == "delete_admin":
                        db.delete_admin(cid=admin_cid)
                        admin_info = await bot.get_chat(chat_id=admin_cid)
                        text = f'🔪 @{admin_info.username} {translator(text="✅ Removed from admin!", dest=lang)}'
                        await bot.send_message(chat_id=admin_cid, text='😪 Your admin rights have been revoked!')
                    else:
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
        await bot.edit_message_text(chat_id=cid, message_id=mid, text=f"<b>{text}</b>", reply_markup=btn)
        await state.set_state(AdminState.add_admin)
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        logging.error(err)
