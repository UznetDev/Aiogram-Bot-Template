import logging
import os
import time
import pandas as pd
from loader import dp, db, bot
from aiogram import types
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from aiogram import F
from aiogram.fsm.context import FSMContext
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from data.config import yil_oy_kun, soat_minut_sekund


@dp.callback_query(IsAdmin(), AdminCallback.filter(F.action == "download_statistika"))
async def download_statistics(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the callback query for generating and sending a statistics file to an admin.

    This function:
    - Verifies if the user has permission to download statistics.
    - Collects user data from the database and creates a DataFrame.
    - Saves the DataFrame to an Excel file and sends it to the requesting admin.
    - Deletes the file after sending.
    - Updates the message with a confirmation or permission error.

    Args:
        call (types.CallbackQuery): The callback query object containing data and user information.
        state (FSMContext): The finite state machine context for managing state data.

    Raises:
        Exception: Logs any errors encountered during the process.

    Returns:
        None
    """
    start_time = time.perf_counter()
    user_id = call.from_user.id
    user_language = call.from_user.language_code
    try:
        message_id = call.message.message_id
        is_admin = SelectAdmin(cid=user_id)

        if is_admin.download_statistika():
            # Retrieve user data from the database
            data = db.select_all_users()
            id_list = []
            cid_list = []
            date_list = []
            usernames = []
            langs = []

            # Populate lists with user data
            for user in data:
                id_list.append(user[0])
                cid_list.append(user[1])
                date_list.append(user[2])
                langs.append(user[3])
                user_info = await bot.get_chat(chat_id=user[1])
                usernames.append(f'@{user_info.username}')

            # Create a DataFrame and save it to an Excel file
            statistics_data = {
                "id": id_list,
                "cid": cid_list,
                "date_add": date_list,
                "username": usernames,
                "lang": langs
            }
            df = pd.DataFrame(statistics_data)
            df.to_excel('data/statistics.xlsx', index=False)

            # Send the Excel file to the user
            document = types.input_file.FSInputFile(path='data/statistics.xlsx')
            user_count = db.stat()
            text = (translator(text="✅ Downloaded! \n\n", dest=user_language) +
                    translator(text="\n👥 Bot users count: ", dest=user_language) +
                    str(user_count) + ' .\n' +
                    translator(text="⏰ Time: ", dest=user_language) +
                    f"{soat_minut_sekund}\n" +
                    translator(text="<b>📆 Date:</b>", dest=user_language) +
                    f" {yil_oy_kun}")

            await bot.send_document(chat_id=user_id, document=document, caption=text)
            os.remove('data/statistics.xlsx')

            # Update the message with confirmation
            text = translator(text="✅ Downloaded!\n", dest=user_language)
            await state.update_data({"message_id": call.message.message_id})
        else:
            # Permission error
            text = translator(text="❌ Unfortunately, you do not have this permission!", dest=user_language)

        await call.message.edit_text(text=f'<b><i>{text}</i></b>', reply_markup=close_btn())
        await state.update_data({"message_id": message_id})
        logging.info(f'Download statistika.',
                      extra={
                          'chat_id': user_id,
                          'language_code': user_language,
                          'execution_time': time.perf_counter() - start_time
                      })

    except Exception as err:
        logging.error(err,
                      extra={
                          'chat_id': user_id,
                          'language_code': user_language,
                          'execution_time': time.perf_counter() - start_time
                      })
