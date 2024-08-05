import logging
import time
import asyncio
import logging
import time
from aiogram import types
from aiogram.fsm.context import FSMContext
from multiprocessing import Process
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from keyboards.inline.admin_btn import main_admin_panel_btn
from keyboards.inline.close_btn import close_btn
from loader import dp, db, bot, file_db
from states.admin_state import AdminState


async def send_message(chat_id, from_chat_id, message_id, caption, reply_markup):
    try:
        await bot.copy_message(chat_id=chat_id,
                               from_chat_id=from_chat_id,
                               message_id=message_id,
                               caption=caption,
                               reply_markup=reply_markup)
        return True
    except Exception as e:
        logging.error(f"Failed to send message to {chat_id}: {e}")
        return False


def send_ads_process(start, from_chat_id, message_id, caption, reply_markup, count_users):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_ads(start, from_chat_id, message_id, caption, reply_markup, count_users))


async def send_ads(start, from_chat_id, message_id, caption, reply_markup, count_users):
    data = {
        "status": True,
        "start": start,
        "done_count": 0,
        "fail_count": 0,
        "start-time": time.time(),
        "from_chat_id": from_chat_id,
        "message_id": message_id,
        "caption": caption,
        "reply_markup": reply_markup,
        "count": count_users
    }
    file_db.add_data(data, key='ads')

    total_users = db.stat()

    # Calculate end index for current batch
    end = min(start + 100, total_users)

    users = db.select_users_by_id(start, end)  # Reverse the list
    logging.info(users)
    for user in users:
        chat_id = user[1]  # Assuming cid is the second column
        result = await send_message(chat_id, from_chat_id, message_id, caption, reply_markup)
        if result:
            data["done_count"] += 1
        else:
            data["fail_count"] += 1
        file_db.add_data(data, key='ads')

    if end < total_users:
        # Schedule the next batch
        await asyncio.sleep(60)  # Sleep for 1 minute
        await send_ads(end, from_chat_id, message_id, caption, reply_markup, count_users)
    else:
        # Finished sending messages
        data["status"] = False
        file_db.add_data(data, key='ads')

        # Send statistics to admin
        stats_message = (
            f"Finished sending messages.\n\n"
            f"Total users: {count_users}\n"
            f"Sent: {data['done_count']}\n"
            f"Failed: {data['fail_count']}\n"
            f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['start-time']))}\n"
            f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
        )
        await bot.send_message(chat_id=from_chat_id, text=stats_message)



@dp.message(AdminState.send_ads, IsAdmin())
async def get_message(msg: types.Message, state: FSMContext):
    try:
        cid = msg.from_user.id
        mid = msg.message_id
        lang = msg.from_user.language_code
        data_state = await state.get_data()
        is_admin = SelectAdmin(cid=cid)
        btn = close_btn()

        if is_admin.send_message():
            ads_status = file_db.reading_db()
            if ads_status['ads'] and ads_status['ads']['status']:
                remaining_time = 60 - (time.time() - ads_status['ads']["start-time"]) % 60

                tx = translator(text=f"Message sending is currently in progress. Please try again in {int(remaining_time)} seconds.",
                                dest=lang)
            else:
                from_chat_id = msg.chat.id
                message_id = msg.message_id
                caption = msg.caption
                reply_markup = msg.reply_markup

                count_users = db.stat()

                process = Process(target=send_ads_process,
                                  args=(0, from_chat_id, message_id, caption, reply_markup, count_users))
                process.start()

                # await state.clear()
                # await msg.answer("Started sending messages.")
                tx = translator(text=f'❌ Unfortunately, you do not have this right!', dest=lang)


        else:
            tx = translator(text=f'Started sending messages.', dest=lang)
            btn = close_btn()
            await state.clear()

        await bot.edit_message_text(chat_id=msg.from_user.id,
                                    message_id=data_state['message_id'],
                                    text=f'<b><i>{tx}</i></b>',
                                    reply_markup=btn)
        await state.update_data({"message_id": mid})

    except Exception as err:
        logging.error(err)

