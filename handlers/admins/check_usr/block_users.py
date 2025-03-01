import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import BlockUser
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState
from data.config import ADMIN


@dp.callback_query(BlockUser.filter(F.action == "block"), IsAdmin())
async def block_users(call: types.CallbackQuery, callback_data: BlockUser, state: FSMContext):
    """
    Handles the blocking and unblocking of users by an admin in a Telegram bot.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing details about the callback.
    - callback_data (BlockUser): Custom data extracted from the callback query, including the user ID to be blocked.
    - state (FSMContext): Finite State Machine context used to manage user states.

    Functionality:
    - Retrieves the user ID from the callback data and the admin's ID from the callback query.
    - Checks if the admin has the authority to block the user using the `SelectAdmin` filter.
    - If the user is not already an admin:
      - Checks if the user is currently banned.
      - If not banned, adds the user to the banned list in the database and sends a notification to the user.
      - If already banned and the banning admin or a super admin is initiating the request, unbans the user.
      - If another admin attempts to unblock, sends a notification that only the blocking admin or a super admin can unblock.
    - Updates the admin's state to `AdminState.check_user` and the state data with the message ID.
    - Sends a message to the admin confirming the action and updates the original message with the result.
    - Logs any exceptions that occur during execution.

    Returns:
    - This function is asynchronous and does not return a value but performs actions such as sending messages and updating states.
    """
    try:
        attention_user_id = callback_data.user_id  # The ID of the user to be blocked/unblocked
        user_id = call.from_user.id  # The ID of the admin issuing the block/unblock command
        mid = call.message.message_id  # The ID of the message triggering the callback
        language_code = call.from_user.language_code  # The language code of the admin for message translation
        data = SelectAdmin(user_id=user_id)  # Check if the admin is authorized to perform the action
        btn = close_btn()  # Inline button to close the message

        if data.block_user():
            check1 = db.select_admin(user_id=attention_user_id)  # Check if the user is an admin
            if check1 is None or user_id == ADMIN:
                check = db.check_user_ban(user_id=attention_user_id)  # Check if the user is already banned
                user = await bot.get_chat(chat_id=attention_user_id)  # Get user details
                if check is None:
                    db.update_user_status(user_id=attention_user_id, 
                                          status='blocked',
                                          updater_user_id=user_id)  # Update user status to blocked
                    text = translator(text='⛔ User blocked\n\n Username: @', dest=language_code)
                    text += str(user.username)
                    await bot.send_message(chat_id=attention_user_id,
                                           text='🚫 You are blocked! If you think this is a mistake, contact the admin.',
                                           reply_markup=close_btn())  # Notify the user of the block
                else:
                    if check['initiator_user_id'] == user_id or check['updater_user_id'] == user_id or user_id == ADMIN:  # Check if the unblocking is authorized
                        db.update_user_status(user_id=attention_user_id,
                                              status='active',
                                              updater_user_id=user_id)  # Update user status to active
                        text = translator(text='✅ User unblocked!\n\n Username: @', dest=language_code)
                        text += str(user.username)
                        await bot.send_message(chat_id=attention_user_id,
                                               text='😊 You are unblocked! Contact the admin.',
                                               reply_markup=close_btn())  # Notify the user of the unblock
                    else:
                        text = translator(text='⭕ Only the person who blocked the user can unblock them!\n\n Username: @', dest=language_code)
                        text += str(user.username)  # Inform that only the original admin can unblock
            else:
                text = translator(text='🚫 I cannot block an admin.', dest=language_code)
                try:
                    db.update_user_status(user_id=attention_user_id,
                                        status='active',
                                        updater_user_id=user_id)  # Ensure user is not mistakenly blocked
                except Exception as err:
                    logging.error(err)  # Log any errors encountered
            await state.set_state(AdminState.check_user)  # Update the FSM state
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=mid,
                                    text=f'<b><i>{text}</i></b>',
                                    reply_markup=btn)  # Edit the original message with the result
        await state.update_data({
            "message_id": call.message.message_id  # Save the message ID in the FSM context
        })
    except Exception as err:
        logging.error(err)  # Log any exceptions that occur
