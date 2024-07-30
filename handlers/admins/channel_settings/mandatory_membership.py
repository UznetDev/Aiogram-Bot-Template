import logging
from loader import dp, bot, DB
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.admin_btn import channel_settings
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator


@dp.callback_query(AdminCallback.filter(F.action == "mandatory_membership"), IsAdmin())
async def mandatory_membership(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        data = SelectAdmin(cid=cid)
        btn = close_btn()

        if data.channel_settings():
            data = DB.reading_db()
            if data['join_channel']:
                text = translator(text='☑️ Forced membership disabled!',
                                  dest=lang)
                join_channel = False
            else:
                text = translator(text='✅ Mandatory membership enabled!',
                                  dest=lang)
                join_channel = True

            DB.change_data(join_channel=join_channel)
            btn = channel_settings(lang=lang)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!',
                              dest=lang)

        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f'<b><i>{text}</i></b>',
                                    reply_markup=btn)
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        logging.error(err)
