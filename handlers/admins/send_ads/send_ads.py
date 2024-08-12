import logging
import time
from loader import dp, file_db
from aiogram import types
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from keyboards.inline.admin_btn import stop_advertisement, main_admin_panel_btn
from aiogram import F
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
        is_admin = SelectAdmin(cid=user_id)
        button_markup = close_btn()

        if is_admin.send_message():
            ads_data = file_db.reading_db().get('ads')

            if ads_data:

                # Calculate remaining users
                remaining_users = ads_data['total_users'] - ads_data['done_count'] - ads_data['fail_count']
                estimated_minutes = (remaining_users / 100)  # 1 minute per 100 users

                # Calculate the estimated end time
                estimated_end_time = time.localtime(time.time() + estimated_minutes * 60)

                message_text = (
                    f"📢 <b>Advertisement Status:</b>\n\n"
                    f"👥 <b>Total users:</b> {ads_data['total_users']}\n"
                    f"✅ <b>Messages sent:</b> {ads_data['done_count']}\n"
                    f"❌ <b>Failed messages:</b> {ads_data['fail_count']}\n"
                    f"⏰ <b>Start Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
                    f"🕒 <b>Estimated End Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', estimated_end_time)}"
                )

                if ads_data['from_chat_id'] == user_id or user_id == ADMIN:
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



