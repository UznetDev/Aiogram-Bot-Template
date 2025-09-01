import os
import pandas as pd
from aiogram import F
from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.filters.admin import IsAdmin
from bot.keyboards.inline.close_btn import close_btn
from bot.keyboards.inline.button import AdminCallback
from bot.data.config import yil_oy_kun, soat_minut_sekund
from bot.loader import dp, db, bot, translator, AM, root_logger



@dp.callback_query(IsAdmin(), AdminCallback.filter(F.action == "download_statistika"))
async def download_statistics(call: types.CallbackQuery, state: FSMContext):

    try:
        user_id = call.from_user.id
        message_id = call.message.message_id
        language = call.from_user.language_code

        if AM(user_id=user_id, feature='view_statistika'):
            data = db.select_all_users()
            id_list = []
            user_id_list = []
            date_list = []
            usernames = []
            langs = []

            # Populate lists with user data
            for user in data:
                id_list.append(user['id'])
                user_id_list.append(user['user_id'])
                date_list.append(user['created_at'])
                langs.append(user['language_code'])
                user_info = await bot.get_chat(chat_id=user['user_id'])
                usernames.append(f'@{user_info.username}')

            # Create a DataFrame and save it to an Excel file
            statistics_data = {
                "id": id_list,
                "user_id": user_id_list,
                "date_add": date_list,
                "username": usernames,
                "lang": langs
            }
            df = pd.DataFrame(statistics_data)
            df.to_excel('data/statistics.xlsx', index=False)

            # Send the Excel file to the user
            document = types.input_file.FSInputFile(path='data/statistics.xlsx')
            user_count = db.stat()
            text = (translator(text="✅ Downloaded! \n\n", dest=language) +
                    translator(text="\n👥 Bot users count: ", dest=language) +
                    str(user_count) + ' .\n' +
                    translator(text="⏰ Time: ", dest=language) +
                    f"{soat_minut_sekund}\n" +
                    translator(text="<b>📆 Date:</b>", dest=language) +
                    f" {yil_oy_kun}")

            await bot.send_document(chat_id=user_id, document=document, caption=text)
            os.remove('data/statistics.xlsx')

            # Update the message with confirmation
            text = translator(text="✅ Downloaded!\n", dest=language)
            await state.update_data({"message_id": call.message.message_id})
        else:
            # Permission error
            text = translator(text="❌ Unfortunately, you do not have this permission!", dest=language)

        await call.message.edit_text(text=f'<b><i>{text}</i></b>', reply_markup=close_btn())
        await state.update_data({"message_id": message_id})

    except Exception as err:
        root_logger.error(err)
