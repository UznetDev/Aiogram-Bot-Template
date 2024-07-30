import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from keyboards.inline.admin_btn import main_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from data.config import ADMIN
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dp.callback_query(IsAdmin(), AdminCallback.filter(F.action == "remove_channel"))
async def remove_channel(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.from_user.id
        mid = call.message.message_id
        lang = call.from_user.language_code
        data = SelectAdmin(cid=cid)
        btn = InlineKeyboardBuilder()
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))

        if data.channel_settings():
            if cid == ADMIN:
                data = db.select_channels()
            else:
                data = db.select_channels_add_cid(add_cid=cid)

            if not data:
                text = translator(text="<b>❔ The channel list is empty!\n\n</b>",
                                  dest=lang)
            else:
                text = translator(text="<b>🔰 Choose a channel:\n\n</b>",
                                  dest=lang)
                count = 0

                for x in data:
                    try:
                        count += 1
                        channel = await bot.get_chat(chat_id=str(-100) + str(x[1]))
                        btn.button(text=f"{channel.full_name}: @{channel.username}",
                                   callback_data=AdminCallback(action="delete_channel", data=str(x[1])).pack())
                        text += (f"<b><i>{count}</i>. Name:</b> <i>{channel.full_name}</i>\n"
                                 f"<b>Username:</b> <i>@{channel.username}</i>\n"
                                 f"<b>Added date:</b> <i>{x[2]}</i>\n\n")
                    except Exception as err:
                        logging.error(err)

            btn.adjust(1)
            btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        else:
            text = translator(text='<b>❌ Unfortunately, you do not have this right!</b>',
                              dest=lang)

        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=mid,
                                    text=text,
                                    reply_markup=btn.as_markup())
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        logging.error(err)
