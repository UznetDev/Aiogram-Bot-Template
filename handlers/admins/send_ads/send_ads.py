import logging
import time
from loader import dp, db
from aiogram import types
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from keyboards.inline.admin_btn import stop_advertisement, main_admin_panel_btn
from aiogram import F
from function.function import format_seconds
from function.send_ads import init_broadcast_settings, send_ads_to_all
from aiogram.fsm.context import FSMContext
from states.admin_state import AdminState
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator
from data.config import ADMIN



@dp.callback_query(AdminCallback.filter(F.action == "send_advertisement"), IsAdmin())
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the "Send Advertisement" button click in the admin panel.

    This function checks if the user is an admin and initiates or updates the advertisement
    sending process. It displays the current status of the advertisement campaign, including
    total users, messages sent, and failed messages. The admin can also stop the advertisement
    if they have the necessary permissions.

    The function utilizes the FSMContext to maintain the state of the operation, allowing it
    to track the progress and handle user interactions effectively. If the user doesn't have
    the required permissions, an error message is displayed.

    Args:
        call (types.CallbackQuery): The callback query from the inline button interaction.
        state (FSMContext): The finite state machine context for handling states within
                            the conversation.

    Returns:
        None: The function sends an appropriate message to the user depending on their
              permissions and the current status of the advertisement campaign.

    Raises:
        Exception: If any error occurs during the execution, it is logged using the logging module.
    """
    try:
        user_id = call.from_user.id
        message_id = call.message.message_id
        language_code = call.from_user.language_code
        is_admin = SelectAdmin(user_id=user_id)
        button_markup = close_btn()

        if is_admin.send_message():
            # users_data = db.select_all_users()
            # users_count = len(users_data)
            # init_broadcast_settings(total=users_count, admin_id=user_id, broadcast_type="users")
            broadcast_status = db.select_setting("broadcast_status")
            if broadcast_status == 'active':
                broadcast_total = int(db.select_setting("broadcast_total"))
                broadcast_sent = int(db.select_setting("broadcast_sent"))
                broadcast_fail = int(db.select_setting("broadcast_fail"))
                broadcast_start_time = float(db.select_setting("broadcast_start_time"))
                broadcast_status = db.select_setting("broadcast_status")
                broadcast_admin_id = int(db.select_setting("broadcast_admin_id"))
                broadcast_start_time = float(db.select_setting("broadcast_start_time"))

                current_time = time.time()
                elapsed = current_time - broadcast_start_time
                processed = broadcast_sent + broadcast_fail
                remaining = broadcast_total - processed
                avg_time = elapsed / processed if processed > 0 else 0
                estimated_remaining = avg_time * remaining


                message_text = (
                    f"📢 <b>Advertisement Status: {broadcast_status}</b>\n\n"
                    f"👥 <b>Total users:</b> {broadcast_total}\n"
                    f"✅ <b>Messages sent:</b> {broadcast_sent}\n"
                    f"❌ <b>Failed messages:</b> {broadcast_fail}\n"
                    f"⏰ <b>Start Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(broadcast_start_time))} \n"
                    f"🕒 <b>Estimated End Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', format_seconds(estimated_remaining))}\n"
                )

                if broadcast_admin_id == user_id or user_id == ADMIN:
                    button_markup = stop_advertisement()
                else:
                    button_markup = main_admin_panel_btn(user_id, language_code)
            else:
                await state.set_state(AdminState.send_ads)

                message_text = translator(
                    text="💬 Send the advertisement...",
                    dest=language_code
                )

            await state.update_data({"message_id": message_id})

        else:
            message_text = translator(
                text="❌ You do not have the necessary permissions!",
                dest=language_code
            )

        await call.message.edit_text(
            text=f'<b><i>{message_text}</i></b>',
            reply_markup=button_markup
        )

        await state.update_data({"message_id": message_id})

    except Exception as err:
        logging.error(err)



