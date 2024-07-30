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
        text = translator(text="<b>🛑 You are not join the channel!:\n\n</b>",
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
                text += f"{son}<b><i></i>. ⭕  {kanals.full_name}</b> <i>@{kanals.username} ❓</i>\n"
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
                                        text=text,
                                        reply_markup=btn.as_markup())
        else:
            # bot_info = await bot.get_me()
            lang = call.from_user.language_code
            text = translator(text='<b>👋Hello dear ',
                              dest=lang) + f' {call.from_user.full_name}\n\n</b>'

            tx = '<b>😎<i> I can download any music ' \
                 'All music with real data.</i></b>\n' \
                 '     🔎<i> I can find music from Instagram, TikTok, Twitter, Threads, Video, Audio.\n' \
                 '      ‼For this, just send me the video address or audio, video file or just send me the song name.\n' \
                 '     🔍 I can also search for music on YouTube.\n' \
                 '     🎙All songs are downloaded in 128 kbps (MP3) and with original artwork.\n' \
                 '     📜if the lyrics are available i can send them!\n\n' \
                 '     ⚠<u>If the audio was uploaded by me first, I will send it instantly, otherwise it may take up to 10 seconds to upload.</u>\n\n' \
                 '     📥 I will post the downloaded audios on my channel. ' \
                 '<b><a href="https://t.me/YouTube_Downs">🔗YouTube</a>\t  ' \
                 '  <a href="https://t.me/Spotify_Music_down">🔗Spotify</a></b>\n\n' \
                 '<b>👩‍💻Help :) Creators channel: <a href="https://t.me/UZ_NET_Coder">UZ_NET_Coder</a></b></i>'
            text += translator(text=tx,
                               dest=lang)

            await bot.edit_message_text(chat_id=cid,
                                        message_id=call.message.message_id,
                                        text=text)
    except Exception as err:
        logging.error(err)
