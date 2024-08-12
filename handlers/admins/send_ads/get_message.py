import asyncio
import logging
import time
from aiogram import types
from aiogram.fsm.context import FSMContext
from concurrent.futures import ProcessPoolExecutor
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from keyboards.inline.admin_btn import main_admin_panel_btn, stop_advertisement
from keyboards.inline.close_btn import close_btn
from loader import dp, db, bot, file_db
from data.config import *
from states.admin_state import AdminState
from cython_code.send_ads import send_ads



@dp.message(AdminState.send_ads, IsAdmin())
async def get_message(msg: types.Message, state: FSMContext):
    """
    Handles the "send_ads" state in the admin panel, checking if the user is an admin and
    updating the advertisement sending process.

    This function retrieves the current state of the advertisement campaign, provides feedback
    to the admin on its progress, and initiates the sending process if necessary.

    Args:
        msg (types.Message): The incoming message from the admin.
        state (FSMContext): The FSM context for managing the conversation state.

    Returns:
        None: Sends a message to the admin with the advertisement process status.

    Raises:
        Exception: Logs any exceptions that occur during execution.
    """
    try:
        # Extract user and message details
        user_id = msg.from_user.id
        message_id = msg.message_id
        language_code = msg.from_user.language_code
        state_data = await state.get_data()

        # Check if the user has admin permissions
        is_admin = SelectAdmin(cid=user_id)

        if is_admin.send_message():
            # Prepare the admin panel button and fetch ads data
            button_markup = main_admin_panel_btn(cid=user_id, lang=language_code)
            ads_data = file_db.reading_db().get('ads')

            if ads_data:
                # If ads are in progress, provide status update

                total_users = ads_data['total_users']
                per_time = ads_data["per_time"]

                # Calculate how many full batches of 100 users are needed
                total_batches = total_users // 100

                # If there are remaining users that don’t fill an entire batch
                if total_users % 100 != 0:
                    total_batches += 1

                # Calculate the total time required for all users
                total_time_required = total_batches * per_time

                # Calculate the estimated end time by adding the total time to the start time
                start_time = ads_data['start-time']
                estimated_end_time = start_time + total_time_required

                # Convert estimated end time to a human-readable format
                estimated_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(estimated_end_time))

                # estimated_end_time = time.localtime(time.time() + estimated_minutes * 60)

                message_text = (
                    f"📢 <b>Advertisement Status:</b>\n\n"
                    f"👥 <b>Total Users:</b> {ads_data['total_users']}\n"
                    f"✅ <b>Messages Sent:</b> {ads_data['done_count']}\n"
                    f"❌ <b>Failed Messages:</b> {ads_data['fail_count']}\n"
                    f"⏰ <b>Start Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
                    f"🕒 <b>Estimated End Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', estimated_end_time)}"
                )
                if ads_data['from_chat_id'] == user_id or user_id == ADMIN:
                    button_markup = stop_advertisement()
            else:
                # If no ads are in progress, start a new ad campaign
                from_chat_id = user_id
                caption = msg.caption
                reply_markup = msg.reply_markup
                total_users = db.stat()

                new_ads_data = {
                    "status": True,
                    "start": 0,
                    "done_count": 0,
                    "fail_count": 0,
                    "start-time": time.time(),
                    "from_chat_id": from_chat_id,
                    "message_id": message_id,
                    "caption": caption,
                    "reply_markup": reply_markup,
                    "total_users": total_users,
                    "per_time": 30
                }

                file_db.add_data(new_ads_data, key='ads')


                # Calculate remaining users
                remaining_users = total_users
                estimated_minutes = (remaining_users / 100)  # 1 minute per 100 users

                # Calculate the estimated end time
                estimated_end_time = time.localtime(time.time() + estimated_minutes * 60)

                message_text = (
                    f"🚀 <b>Started sending to {total_users} users.</b>\n\n"
                    f"⏰ <b>Start Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
                    f"🕒 <b>Estimated End Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', estimated_end_time)}"
                )

                # Start the ad sending process in a separate thread
                time.sleep(1)
                loop = asyncio.get_event_loop()
                executor_pool = ProcessPoolExecutor()
                loop.run_in_executor(executor_pool, send_ads)

        else:
            # If the user is not an admin, send a permission error message
            message_text = translator(
                text="❌ Unfortunately, you do not have this permission!",
                dest=language_code
            )
            button_markup = close_btn()
            await state.clear()

        # Update the message with the new content and buttons
        await bot.edit_message_text(
            chat_id=msg.from_user.id,
            message_id=state_data['message_id'],
            text=f'<b><i>{message_text}</i></b>',
            reply_markup=button_markup
        )

        # Update the state with the current message ID
        await state.update_data({"message_id": message_id})

    except Exception as err:
        logging.error(f"Error in get_message: {err}")

