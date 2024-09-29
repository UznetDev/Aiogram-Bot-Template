import logging
import time
from loader import dp, bot, db
from aiogram import types
from keyboards.inline.close_btn import close_btn
from keyboards.inline.admin_btn import block_user
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from states.admin_state import AdminState


@dp.message(AdminState.check_user, IsAdmin())
async def attach_user(msg: types.Message, state: FSMContext):
    """
    Handles user blocking or unblocking based on the provided user ID.

    This function:
    - Verifies if the user has admin permissions to block or unblock users.
    - Processes the user ID provided in the message.
    - Checks if the user is already blocked or in the admin list.
    - Updates the message to reflect the result of the operation and provides relevant feedback to the admin.

    Args:
        msg (types.Message): The message object that contains the user ID and other metadata.
        state (FSMContext): The finite state machine context for managing state data.

    Raises:
        Exception: Logs any errors encountered during processing.

    Returns:
        None
    """
    start_time = time.perf_counter()
    user_id = msg.from_user.id  # Chat ID of the admin
    message_id = msg.message_id  # Message ID of the current message
    language_code = msg.from_user.language_code  # Language code of the admin
    try:
        log = 'Action on attach user, '
        is_admin = SelectAdmin(user_id=user_id)  # Check admin permissions
        target_user_id = int(msg.text)  # Extract user ID from the message
        btn = close_btn()  # Initialize the close button
        text = translator(text="🔴 Something went wrong!\n", dest=language_code)  # Default error message

        if is_admin.block_user():
            data_state = await state.get_data()  # Get the current state data
            try:
                user = await bot.get_chat(chat_id=target_user_id)  # Get user information
                check = db.check_user_ban(user_id=target_user_id)  # Check if the user is banned
                check1 = db.check_user(cid=target_user_id)  # Check if the user exists in the bot's list

                if check1 is not None:
                    btn = block_user(cid=user_id, user_id=target_user_id, lang=language_code)  # Button for blocking/unblocking user
                    if check is None:
                        check2 = db.select_admin(cid=target_user_id)  # Check if the user is an admin
                        select_user = db.check_user(user_id)  # Get information about the user

                        if check2 is None:
                            # User is successfully unblocked
                            text = "✅ User unblocked!"
                            text += translator(text=f'\n\nUsername: @', dest=language_code) + user.username
                            text += translator(text='\nLanguage code: ', dest=language_code) + f'{select_user[3]}'
                        else:
                            # User is blocked but is an admin
                            tx = "✅ User blocked!\n👮‍♂️ User is in the list of admins!</b>"
                            text = translator(text=f'{tx}\n\nUsername: @', dest=language_code) + user.username
                            text += translator(text='<b>\nLanguage code:</b> ', dest=language_code) + f'<i>{select_user[3]}</i>'
                    else:
                        # User is already blocked
                        tx = "✅ User blocked!\n Date:"
                        text = translator(text=f'{tx} {check[3]}\n\nUsername: @', dest=language_code) + user.username
                else:
                    # User not found in the bot's list
                    text = translator(text="🔴 User not found!\nThe user may not be in the bot's list..", dest=language_code)
                    log += 'but user not found, '
            except Exception as err:
                logging.warning(err,
                                extra={
                                      'chat_id': user_id,
                                      'language_code': language_code,
                                      'execution_time': time.perf_counter() - start_time
                              })
                text = translator(text="🔴 User not found!\nThe bot may not have found the user..",
                                  dest=language_code)
            finally:
                # Update the message with the result and provide the close button
                await bot.edit_message_text(chat_id=user_id,
                                            message_id=data_state['message_id'],
                                            text=f'<b><i>{text}</i></b>',
                                            reply_markup=btn)
        else:
            # User does not have permission to block/unblock users
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)
            log += 'but do not have permission, '

        # Edit the original message to reflect the result
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=message_id,
                                    text=f'<b><i>{text}</i></b>',
                                    reply_markup=btn)
        await state.update_data({"message_id": message_id})  # Update state data
        await bot.delete_message(chat_id=user_id, message_id=message_id)  # Delete the original message
        logging.info(log,
                      extra={
                          'chat_id': user_id,
                          'language_code': language_code,
                          'execution_time': time.perf_counter() - start_time
                      })
    except Exception as err:
        # Log any exceptions that occur
        logging.error(err,
                      extra={
                          'chat_id': user_id,
                          'language_code': language_code,
                          'execution_time': time.perf_counter() - start_time
                      })

