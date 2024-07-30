import logging
from aiogram import types
from aiogram.filters import CommandStart, CommandObject
from function.translator import translator
from loader import *
from data.config import yil_oy_kun, soat_minut_sekund
from keyboards.inline.user import send_url
from keyboards.inline.user import share_audio


@dp.message(CommandStart())
async def start_handler(msg: types.Message, command: CommandObject):
    try:
        cid = msg.from_user.id
        lang = msg.from_user.language_code
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        first_name = msg.from_user.first_name
        text = (f'<b>👋Hello dear %s</b>\n'
                f'<b><i>⤐ Send me one of the following and I will upload the full song for you.</i></b>\n'
                f"    	<i>๏ The name of the song.\n"
                f"    	๏ A video.\n"
                f"    	๏ A audio.\n"
                f"    	๏ A voice message.\n"
                f"    	๏ A video message.\n"
                f"    	๏ A TikTik video link.\n"
                f"    	๏ A Instagram video link.\n"
                f"    	๏ A Twitter video link.\n"
                f"    	๏ A %s video link.</i>\n\n"
                f"<b>⸎ Download music from these social networks without searching. </b><i>\n"
                f"       ๏ A Youtube video link..\n"
                f"       ๏ A Spotify video link.</i>\n\n"
                f"<b><i>⚠More information and options: /help\n"
                f"☕Bot Creator: <a href='https://t.me/uznet_dev'>UZNet Dev</a></i></b>\n"
                f"<b><i>ↈ For more information and questions:\n"
                f"       ⤐ <a href='https://t.me/TG_administrator_Call'> TG administrator</a></i></b>\n\n"
                f"<b><i>@%s</i></b>")
        tx = translator(text=f'I found a great bot, give it a try\n',
                        dest=lang)
        btn = send_url(url=f'{tx} https://t.me/{bot_username}?start',
                       lang=lang)
        try:
            tr_text = translator(text=text,
                                 dest=lang)
            tr_text = tr_text % (first_name, 'Threads', bot_username)
            await msg.answer(tr_text,
                             reply_markup=btn)
        except:
            text = text % (first_name, 'Threads', bot_username)
            await msg.answer(text,
                             reply_markup=btn)
        try:
            if db.check_user(cid=cid) is None:
                db.add_user(cid=cid,
                            date=str(yil_oy_kun) + ' / ' + str(soat_minut_sekund),
                            lang=lang)
                text = (f"<b>%s  \n"
                        f"👋Hello, dear %s,\n first of all, thank you for choosing the @%s.\n"
                        f"♕Get to know @%s features.\n"
                        f"♬ Through @%s you can find any kind of music.\n"
                        f"⸎In order for the @%s to find the full form of the music, you need to send it one of the following.</b><i>\n"
                        f"    	๏. The name of the song.\n"
                        f"    	๏ A video.\n"
                        f"    	๏ A audio.\n"
                        f"    	๏ A voice message.\n"
                        f"    	๏ A video message.\n"
                        f"    	๏ A TikTik video link.\n"
                        f"    	๏ A Instagram video link.\n"
                        f"    	๏ A Twitter video link.\n"
                        f"    	๏ A %s video link.</i>\n\n"
                        f"<b>⸎ Download music from these social networks without searching. </b><i>\n"
                        f"      ๏ Youtube video link..\n"
                        f"      ๏ Spotify video link.</i>\n\n"
                        f"<b>⤐ @%s can also search for music on Youtube and Spotify! \n"
                        f"If you can't find the music through the main search, you can search through the YouTube or Spotify search engine. \n"
                        f"To search through the YouTube and Spotify search engines, you first use the main search engine,"
                        f"and use the buttons below the search engine.</b>\n\n"
                        f"<b>⚡The songs found through the main search engine will be downloaded in 1 or 2 seconds,\n\n"
                        f"⚒ Loading a song through the Spotify and YouTube search engine can"
                        f" take up to 10 seconds if you are the first to download this song.\n"
                        f"This will take 1 or 2 seconds if the song has been downloaded before.</b>\n\n"
                        f"<b>♬ Songs downloaded from Spotify and Youtube are uploaded in 120 kbps quality and with real data. "
                        f"Except for downloads from the main search engine..</b>\n\n\n"
                        f"<b>♕ Through the main search system, up to 5,000 songs are searched at one time,"
                        f" songs can be selected through the buttons below.\n"
                        f"♕ Top 10 songs are selected when searched on Spotify and YouTube.</b>\n\n"
                        f"<b>🧨All in one service, the service is absolutely free in unlimited quantities.\n"
                        f"☏This bot is created so that you can find the music you want without difficulty.\n"
                        f"⸿To support us, please share the bot with your friends.</b>\n\n"
                        f"<b>📥 I will post the downloaded audios on my channel. </b>\n"
                        f"       <i><a href='https://t.me/YouTube_Downs'>🔗YouTube</a>\n"
                        f"       <a href='https://t.me/Spotify_Music_down'>🔗Spotify</a>\n"
                        f"       <a href='https://t.me/musiqa_skachat'>🔗Music</a>\n"
                        f"       <a href='https://t.me/thefmmusic'>🔗Fm Music</a>\n\n</i>"
                        f"<b><i>ↈ For more information and questions:\n"
                        f"       ⤐ <a href='https://t.me/TG_administrator_Call'> TG administrator</a>\n"
                        f"For discussion: \n"
                        f"       ⤐ <a href='https://t.me/The_code_team'> The code team</a>\n"
                        f"☕Bot Creator: <a href='https://t.me/uznet_dev'>UZNet Dev</a></i></b>\n\n"
                        f"<b><i><u>%s \n</u></i></b>")

                tx = translator(text=f'I found a great bot, give it a try.\n',
                                dest=lang)
                btn = send_url(url=f'{tx} https://t.me/{bot_info.username}?start',
                               lang=lang)
                try:
                    tr_text = translator(text=text,
                                         dest=lang)
                    tr_text = tr_text % (
                        f" ⇐ {bot_info.full_name.upper()} ⇒  ".center(50, '-'), first_name, bot_username, bot_username,
                        bot_username, bot_username, "Threads", bot_username, f" @{bot_username} ".center(50, '-'))
                    await msg.answer(tr_text,
                                     reply_markup=btn)
                except:
                    text = text % (
                        f" ⇐ {bot_info.full_name.upper()} ⇒  ".center(50, '-'), first_name, bot_username, bot_username,
                        bot_username, bot_username, "Threads", bot_username, f" @{bot_username} ".center(50, '-'))
                    await msg.answer(text,
                                     reply_markup=btn)
        except Exception as err:
            logging.error(err)
        try:
            args = command.args
            if args:
                check = music_db.check_music(text)
                if check:
                    size = round(int(check[10]) / (1024 * 1024), 2)
                    duration = round(int(check[4]) / 60, 2)
                    caption = (f'<i>💾 {size} </i><b>Mb</b>'
                               f'<u>🕐 {str(duration).replace(".", ":")} <b>Ms</b></u>\n\n'
                               f"<b><i>📥 @{bot_info.username}</i></b>")
                    btn = share_audio(text, 'en')
                    await bot.send_audio(chat_id=cid,
                                         audio=f'https://t.me/song_cloud_db/{check[1]}',
                                         performer=check[5] or bot_info.username,
                                         title=check[7] or bot_info.username,
                                         caption=caption or bot_info.username,
                                         reply_markup=btn)
        except:
            pass
    except Exception as err:
        logging.error(err)
