import logging
import time
from data.config import ADMIN
from loader import dp, file_db
from aiogram import types
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from aiogram import F
from aiogram.fsm.context import FSMContext
from states.admin_state import AdminState
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator


@dp.callback_query(AdminCallback.filter(F.action == "stop_ads"), IsAdmin())
async def stop_ads(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the "Stop Advertisement" button click in the admin panel.

    This function stops the ongoing advertisement campaign if the user has the required
    permissions. It updates the campaign status and provides a summary of the operation.
    If the user is not authorized, an error message is displayed.

    Args:
        call (types.CallbackQuery): The callback query from the inline button interaction.
        state (FSMContext): The finite state machine context for handling states within the conversation.

    Returns:
        None: The function sends an appropriate message to the user depending on their permissions
              and the current status of the advertisement campaign.

    Raises:
        Exception: If any error occurs during execution, it is logged using the logging module.
    """
    try:
        # Extract user and message details
        user_id = call.from_user.id
        message_id = call.message.message_id
        language_code = call.from_user.language_code

        # Check if the user has admin permissions
        is_admin = SelectAdmin(cid=user_id)

        if is_admin.send_message():
            # Fetch the current ads data
            ads_data = file_db.reading_db().get('ads')

            if ads_data:
                # Check if the user has permission to stop the ads (creator or global admin)
                if ads_data['from_chat_id'] == user_id or user_id == ADMIN:
                    file_db.add_data(False, key='ads')
                    summary_text = (
                        f"📬 <b>Advertisement Sending Stopped</b>\n\n"
                        f"👥 <b>Total Users:</b> {ads_data['total_users']}\n"
                        f"✅ <b>Sent:</b> {ads_data['done_count']}\n"
                        f"❌ <b>Failed:</b> {ads_data['fail_count']}\n"
                        f"⏳ <b>Start Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ads_data['start-time']))}\n"
                        f"🕒 <b>End Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}"
                    )
                else:
                    # If the user doesn't have permission to stop the ads
                    summary_text = translator(
                        text="❌ You do not have permission to stop this process!",
                        dest=language_code
                    )
            else:
                # If no ads data is found, assume the campaign has ended or doesn't exist
                await state.set_state(AdminState.send_ads)
                summary_text = translator(
                    text="⚠️ Advertisement not found!",
                    dest=language_code
                )

            await state.update_data({"message_id": message_id})
        else:
            # If the user is not an admin
            summary_text = translator(
                text="❌ Unfortunately, you do not have this permission!",
                dest=language_code
            )

        # Update the message text and close the inline buttons
        await call.message.edit_text(
            text=f'<b><i>{summary_text}</i></b>',
            reply_markup=close_btn()
        )

        # Update the state with the current message ID
        await state.update_data({"message_id": message_id})

    except Exception as err:
        # Log any errors that occur during the process
        logging.error(f"Error in stop_ads: {err}")
