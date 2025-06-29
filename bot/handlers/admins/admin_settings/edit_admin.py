from aiogram import types, F
from aiogram.fsm.context import FSMContext

from bot.data.config import ADMIN
from bot.filters.admin import IsAdmin
from bot.function.function import x_or_y
from bot.keyboards.inline.close_btn import close_btn
from bot.loader import dp, bot, db, root_logger, translator, AM
from bot.states.admin_state import AdminState
from bot.keyboards.inline.button import EditAdminSetting
from bot.keyboards.inline.admin_btn import attach_admin_btn


@dp.callback_query(EditAdminSetting.filter(F.action == "edit"), IsAdmin())
async def edit_admin(call: types.CallbackQuery, callback_data: EditAdminSetting, state: FSMContext):
    try:
        user_id = call.from_user.id
        mid = call.message.message_id
        language_code = call.from_user.language_code
        target_user_id = callback_data.user_id
        edit_key = callback_data.data
        btn = close_btn()

        if AM(user_id=user_id, feature='add_admin'):
            is_admin, initiator_user_id, role, created_at  = AM.__getitem__(target_user_id)
            if not is_admin:
                text = f'⛔{target_user_id} {translator(text="😪 Not available in admin list!", dest=language_code)}'
            else:
                if initiator_user_id == user_id or user_id == ADMIN:
                    if edit_key == "delete_admin":
                        AM.remove(user_id=target_user_id, initiator_user_id=user_id)
                        admin_info = await bot.get_chat(chat_id=target_user_id)
                        text = f'🔪 @{admin_info.username} {translator(text="✅ Removed from admin!", dest=language_code)}'
                        await bot.send_message(chat_id=target_user_id, text='😪 Your admin rights have been revoked!')
                    else:
                        feature = AM(user_id=edit_key, feature=edit_key)
                        value = False if feature else True
                        AM.update(user_id=target_user_id, feature=edit_key, value=value, initiator_user_id=user_id)

                        btn = attach_admin_btn(user_id=target_user_id, language_code=language_code)
                        
                        text = '<b>👮 Change saved!</b>\n\n'
                        for feature in AM.list_features():
                               text += f"<b>{feature['name']}</b>: <i>{x_or_y(AM(user_id=user_id, feature=feature['key']))}</i>\n"

                else:
                    text = translator(text='🛑 You can only change the admin rights you assigned!', dest=language_code)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)

        await bot.edit_message_text(chat_id=user_id, message_id=mid, text=f"<b>{text}</b>", reply_markup=btn)
        await state.set_state(AdminState.add_admin)
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        root_logger.error(err)

