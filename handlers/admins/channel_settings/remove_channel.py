import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from keyboards.inline.admin_btn import main_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from function.translator import translator
from data.config import ADMIN
from aiogram.utils.keyboard import InlineKeyboardBuilder

@dp.callback_query(IsAdmin(), AdminCallback.filter(F.action == "remove_channel"))
async def remove_channel(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the removal of channels by displaying a list of channels and allowing the admin to choose one to delete.

    Parameters:
    - call (types.CallbackQuery): The callback query object containing information about the user's action.
    - state (FSMContext): The FSM context to manage the bot's state during the conversation.

    Functionality:
    - Retrieves the admin's user ID (`cid`), the message ID (`mid`), and the language code (`lang`) from the callback query.
    - Checks if the user has the necessary permissions to access channel settings using the `SelectAdmin` filter.
    - If authorized, retrieves the list of channels either for all admins (if the user is the main admin) or for channels added by the specific admin.
    - If the channel list is empty, informs the admin. If not, displays a list of channels with options to delete them.
    - Creates an inline keyboard with buttons to choose channels for deletion and a close button.
    - Updates the message in the chat with the channel list and the inline keyboard.

    Returns:
    - This function is asynchronous and does not return a value. It interacts with the Telegram API to update messages and with the database to retrieve channel information.
    """
    try:
        cid = call.from_user.id  # The ID of the admin who initiated the action
        mid = call.message.message_id  # The ID of the message to be updated
        lang = call.from_user.language_code  # The language code for translation
        data = SelectAdmin(cid=cid)  # Check if the user has admin permissions
        btn = InlineKeyboardBuilder()  # Create an instance of InlineKeyboardBuilder for the keyboard

        # Attach the main button to the keyboard
        btn.attach(InlineKeyboardBuilder.from_markup(main_btn()))

        if data.channel_settings():
            # Retrieve the list of channels based on admin permissions
            if cid == ADMIN:
                data = db.select_channels()
            else:
                data = db.select_channels_add_cid(add_cid=cid)

            if not data:
                # Inform the admin if no channels are available
                text = translator(text="❔ The channel list is empty!\n\n", dest=lang)
            else:
                # Display the list of channels with options to delete them
                text = translator(text="🔰 Choose a channel:\n\n", dest=lang)
                count = 0

                for x in data:
                    try:
                        count += 1
                        channel = await bot.get_chat(chat_id=str(-100) + str(x[1]))
                        # Add a button for each channel to the keyboard
                        btn.button(text=f"{channel.full_name}: @{channel.username}",
                                   callback_data=AdminCallback(action="delete_channel", data=str(x[1])).pack())
                        text += (f"<b><i>{count}</i>. Name:</b> <i>{channel.full_name}</i>\n"
                                 f"<b>Username:</b> <i>@{channel.username}</i>\n"
                                 f"<b>Added date:</b> <i>{x[2]}</i>\n\n")
                    except Exception as err:
                        # Log errors if channel information cannot be retrieved
                        logging.error(err)

            # Adjust the keyboard layout and attach the close button
            btn.adjust(1)
            btn.attach(InlineKeyboardBuilder.from_markup(close_btn()))
        else:
            # Inform the admin if they do not have the right to access channel settings
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=lang)

        # Edit the message with the updated text and keyboard
        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=mid,
                                    text=f'{text}',
                                    reply_markup=btn.as_markup())
        # Update FSM state with the current message ID
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        # Log any errors that occur during the execution
        logging.error(err)

