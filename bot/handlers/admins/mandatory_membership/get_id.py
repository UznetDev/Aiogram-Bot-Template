import logging
from loader import dp, bot, db
from aiogram import types
from keyboards.inline.admin_btn import channel_settings
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from api.translator import translator
from states.admin_state import AdminState
from data.config import yil_oy_kun, soat_minut_sekund

@dp.message(AdminState.add_channel, IsAdmin())
async def add_channel2(msg: types.Message, state: FSMContext):
    try:
        user_id = msg.from_user.id  # The ID of the admin making the request
        mid = msg.message_id  # The ID of the message associated with the request
        language_code = msg.from_user.language_code  # The language code for translating responses
        data = SelectAdmin(user_id=user_id)  # Check if the user has admin permissions
        btn = close_btn()  # A button for closing the message
        data_state = await state.get_data()  # Get data stored in the FSM state

        if data.channel_settings():
            try:
                tx = msg.text  # The text message containing the channel ID
                k_id = int(str(-100) + str(tx))  # Format the channel ID for API
                channel = await bot.get_chat(chat_id=k_id)  # Get channel details using the Telegram API
                check = db.check_channel(channel_id=tx)  # Check if the channel is already in the database

                if check is None:
                    # Add the channel to the database if it doesn't exist
                    db.insert_channel(channel_id=tx,
                                      initiator_user_id=user_id)
                    text = translator(text="✅ The channel was successfully added\n", dest=language_code)
                    text += f"<b>Name:</b> <i>{channel.full_name}</i>\n" \
                            f"<b>Username:</b> <i>@{channel.username}</i>"
                else:
                    # Inform the user if the channel is already in the database
                    text = translator(text="✅ The channel was previously added\n", dest=language_code)
                    text += f"<b>Name:</b> <i>{channel.full_name}</i>\n" \
                            f"<b>Username:</b> <i>@{channel.username}</i>\n" \
                            f"<b>Added date:</b> <i>{check['created_at']}</i>"

                btn = channel_settings(language_code=language_code)  # Update the button for channel settings
            except Exception as err:
                # Handle exceptions such as the bot not being an admin in the channel
                text = translator(text="🔴 The channel could not be added because the channel was not found!\n"
                                       "The bot is not an admin on the channel.", dest=language_code)
                logging.error(err)
            await state.clear()  # Clear the FSM state
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)

        # Update the message with the result and close button
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=data_state['message_id'],
                                    text=f'{text}',
                                    reply_markup=btn)
        await state.update_data({
            "message_id": mid
        })  # Update FSM state with the current message ID
    except Exception as err:
        logging.error(err)  # Log any errors that occur during the process
