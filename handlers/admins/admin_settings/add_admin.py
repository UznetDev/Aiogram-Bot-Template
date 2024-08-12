import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from filters.admin import IsAdmin, SelectAdmin
from function.translator import translator
from keyboards.inline.admin_btn import admin_setting
from keyboards.inline.close_btn import close_btn
from loader import dp, bot, db
from states.admin_state import AdminState
from data.config import yil_oy_kun, soat_minut_sekund

@dp.message(AdminState.add_admin, IsAdmin())
async def add_admin(msg: types.Message, state: FSMContext):
    """
    Handles the addition of a new admin to the system.

    Parameters:
    - msg (types.Message): The message object containing the admin ID to be added.
    - state (FSMContext): The FSM context to manage the bot's state during the conversation.

    Functionality:
    - Retrieves the admin's user ID (`cid`), the message ID (`mid`), and the language code (`lang`) from the message.
    - Checks if the sender has the required permissions to add an admin.
    - Tries to add the new admin using the provided user ID:
        - If the admin is successfully added, sends a confirmation message to both the current admin and the newly added admin.
        - If the admin was previously added, sends an appropriate message with existing details.
    - Updates the message with a response based on the success or failure of the operation.

    Returns:
    - This function is asynchronous and does not return a value. It interacts with the Telegram API to update messages and manage the state.

    Error Handling:
    - Catches and logs any exceptions that occur during the addition of the new admin or message editing.
    """
    try:
        cid = msg.from_user.id  # The ID of the admin who is performing the action
        mid = msg.message_id  # The ID of the message to be updated
        lang = msg.from_user.language_code  # The language code for translation
        data = SelectAdmin(cid=cid)  # Retrieves admin settings for the current user
        add_admin_db = data.add_admin()  # Check if the user has the right to add an admin
        user_id = int(msg.text)  # The ID of the user to be added as an admin

        if add_admin_db:
            data_state = await state.get_data()  # Get current state data
            btn = await admin_setting(cid=cid, lang=lang)  # Prepare admin settings buttons
            text = "🔴 Admin failed because admin was not found!\n"

            try:
                user = await bot.get_chat(chat_id=user_id)  # Get user information
                check = db.select_admin(cid=user_id)  # Check if the user is already an admin

                if check is None:
                    # Add the new admin to the database
                    db.add_admin(cid=user_id,
                                 date=f"{yil_oy_kun} / {soat_minut_sekund}",
                                 add=cid)
                    text = translator(text="✅ Admin has been successfully added\n\nName: ",
                                      dest=lang)
                    text += f"{user.full_name}\n"
                    text += f'Username:  @{user.username}\n'
                    await bot.send_message(chat_id=user_id,
                                           text=f'😊Hi @{user.username}, you have been made an admin\n'
                                                f'To open the panel, use /admin ',
                                           reply_markup=close_btn())
                    btn = await admin_setting(cid=cid, lang=lang)  # Prepare admin settings buttons
                else:
                    text = translator(text="✅ Admin was added before\n\nName: ",
                                      dest=lang)
                    text += f"{user.full_name}\n"
                    text += f'Username:  @{user.username}\n'
                    text += translator(text="Add date: ",
                                       dest=lang)
                    text += f'{check[9]}\n<code>{check[2]}</code>'
                    text += translator(text="Added by",
                                       dest=lang)
            except Exception as err:
                logging.error(err)  # Log any errors that occur
                text = translator(text="🔴 Admin failed because admin was not found!\n"
                                       "The bot may not have found the admin..",
                                  dest=lang)
            finally:
                text = translator(text=text,
                                  dest=lang)
                await bot.edit_message_text(chat_id=cid,
                                            message_id=data_state['message_id'],
                                            text=text,
                                            reply_markup=btn)
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!',
                              dest=lang)
            btn = close_btn()
        await bot.edit_message_text(chat_id=cid,
                                    message_id=mid,
                                    text=f"<b>{text}</b>",
                                    reply_markup=btn)
        await state.update_data({
            "message_id": mid
        })
    except Exception as err:
        logging.error(err)  # Log any errors that occur

