from aiogram import types, F
from aiogram.fsm.context import FSMContext

from bot.data.config import ADMIN
from bot.filters.admin import IsAdmin
from bot.function.function import x_or_y
from bot.keyboards.inline.admin_btn import attach_admin_btn
from bot.keyboards.inline.button import AdminSetting
from bot.keyboards.inline.close_btn import close_btn
from bot.loader import dp, bot, root_logger, translator, AM
from bot.states.admin_state import AdminState



@dp.callback_query(AdminSetting.filter(F.action == "attach_admin"), IsAdmin())
async def attach_admins(call: types.CallbackQuery, callback_data: AdminSetting, state: FSMContext):

    try:
        user_id = call.from_user.id
        mid = call.message.message_id
        language_code = call.from_user.language_code
        target_user_id = callback_data.user_id
        btn = close_btn()

        if AM(user_id=user_id, feature='admin_settings'):
            is_admin, initiator_user_id, role, created_at  = AM[target_user_id]
            if initiator_user_id == user_id or user_id == ADMIN:
                btn = attach_admin_btn(user_id=target_user_id, 
                                       language_code=language_code)
                
                text = f'<b>👮‍♂️Admin rights!</b>\n\n' 
                for f in AM.list_features():
                       text += f"<b>{f['name']}:</b> <i>{x_or_y(AM(user_id=target_user_id, feature=f['key']))}</i>\n"
            else:
                text = translator(text='😪You can only change the admin rights you added!', dest=language_code)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)

        await bot.edit_message_text(chat_id=user_id, message_id=mid, text=f'{text}', reply_markup=btn)
        await state.set_state(AdminState.add_admin)
        await state.update_data({"message_id": call.message.message_id})
    except Exception as err:
        root_logger.error(err)
