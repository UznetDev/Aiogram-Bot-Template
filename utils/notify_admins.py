import logging,os
from loader import bot
from data.config import ADMIN, log_file_name
from keyboards.inline.close_btn import close_btn
from aiogram import types


async def on_startup_notify():
    try:
        await bot.send_message(chat_id=ADMIN,
                               text="<b>Bot ishga tushdi!\n</b>"
                                    "<b>Admin panelni ochish /admin\n</b>"
                                    "<i>Maxsus faqat siz uchun /stat buyrug'i</i>",
                               reply_markup=close_btn())
        try:
            if os.path.exists(log_file_name) and os.path.getsize(log_file_name):
                try:
                    document = types.input_file.FSInputFile(path=log_file_name)
                    await bot.send_document(chat_id=ADMIN,
                                            document=document,
                                            caption=f'<b>Update log</b>')
                    if (os.path.getsize(log_file_name)) * (1024 * 124) > 40:
                        os.remove(log_file_name)
                except Exception as err:
                    logging.error(err)
        except Exception as Err:
            logging.exception(Err)

    except Exception as err:
        logging.error(err)
