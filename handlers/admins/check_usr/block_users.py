import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import BlockUser
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState
from data.config import yil_oy_kun, soat_minut_sekund, ADMIN

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
        user_id = callback_data.cid  # The ID of the user to be blocked/unblocked
        cid = call.from_user.id  # The ID of the admin issuing the block/unblock command
        mid = call.message.message_id  # The ID of the message triggering the callback
        lang = call.from_user.language_code  # The language code of the admin for message translation
        data = SelectAdmin(cid=cid)  # Check if the admin is authorized to perform the action
        btn = close_btn()  # Inline button to close the message

        if data.block_user():
            check1 = db.select_admin(cid=user_id)  # Check if the user is an admin
            if check1 is None:
                check = db.check_user_ban(cid=user_id)  # Check if the user is already banned
                user = await bot.get_chat(chat_id=user_id)  # Get user details
                if check is None:
                    db.add_user_ban(cid=user_id,
                                    admin_cid=cid,
                                    date=f'{yil_oy_kun} / {soat_minut_sekund}')  # Add user to ban list
                    text = translator(text='⛔ User blocked\n\n Username: @', dest=lang)
                    text += str(user.username)
                    await bot.send_message(chat_id=user_id,
                                           text='🚫 You are blocked! If you think this is a mistake, contact the admin.',
                                           reply_markup=close_btn())  # Notify the user of the block
                else:
                    if check[2] == cid or cid == ADMIN:  # Check if the unblocking is authorized
                        db.delete_user_ban(cid=user_id)  # Remove user from ban list
                        text = translator(text='✅ User unblocked!\n\n Username: @', dest=lang)
                        text += str(user.username)
                        await bot.send_message(chat_id=user_id,
                                               text='😊 You are unblocked! Contact the admin.',
                                               reply_markup=close_btn())  # Notify the user of the unblock
                    else:
                        text = translator(text='⭕ Only the person who blocked the user can unblock them!\n\n Username: @', dest=lang)
                        text += str(user.username)  # Inform that only the original admin can unblock
            else:
                text = translator(text='🚫 I cannot block an admin.', dest=lang)
                try:
                    db.delete_user_ban(cid=user_id)  # Ensure user is not mistakenly banned
                except Exception as err:
                    logging.error(err)  # Log any errors encountered
            await state.set_state(AdminState.check_user)  # Update the FSM state
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=lang)
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f'<b><i>{text}</i></b>',
                                    reply_markup=btn)  # Edit the original message with the result
        await state.update_data({
            "message_id": call.message.message_id  # Save the message ID in the FSM context
        })
    except Exception as err:
        logging.error(err)  # Log any exceptions that occur
