import logging
from loader import dp, bot, db
from aiogram import types, F
from function.translator import translator
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.inline.button import MainCallback


@dp.callback_query(MainCallback.filter(F.action == "check_join"))
async def check_join(call: types.CallbackQuery):
    try:
        cid = call.from_user.id
        lang = call.from_user.language_code
        ruyxat = db.select_channels()
        btn = InlineKeyboardBuilder()
        text = translator(text="🛑 You are not join the channel!:\n\n",
                          dest=lang)
        text1 = translator(text="🛑 You are not join the channel!:\n\n",
                           dest=lang)
        son = 0
        force = False
        for x in ruyxat:
            ids = str(-100) + str(x[1])
            kanals = await bot.get_chat(ids)
            try:
                res = await bot.get_chat_member(chat_id=ids, user_id=cid)
            except:
                continue
            if res.status == 'member' or res.status == 'administrator' or res.status == 'creator':
                pass
            else:
                force = True
                son += 1
                text += f"\n{son}<b><i></i>. ⭕  {kanals.full_name}</b> <i>@{kanals.username} ❓</i>\n"
                btn.button(text='➕ ' + kanals.title,
                           url=f"{await kanals.export_invite_link()}")
        btn.button(text=translator(text='♻ Check!', dest=lang),
                   callback_data=MainCallback(action="check_join", q='').pack())
        btn.adjust(1)
        if force:

            await call.answer(text=text1,
                              reply_markup=btn.as_markup())
            await bot.edit_message_text(chat_id=cid,
                                        message_id=call.message.message_id,
                                        text=f"<b>{text}</b>",
                                        reply_markup=btn.as_markup())
        else:
            lang = call.from_user.language_code
            text = translator(text='Same text',
                              dest=lang)
            await bot.edit_message_text(chat_id=cid,
                                        message_id=call.message.message_id,
                                        text=text)
    except Exception as err:
        logging.error(err)
