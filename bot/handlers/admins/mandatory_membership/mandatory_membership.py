from aiogram import types, F
from aiogram.fsm.context import FSMContext


from bot.data.config import ADMIN
from bot.filters.admin import IsAdmin
from bot.loader import dp, bot, db, translator, root_logger, AM, MMM
from bot.keyboards.inline.close_btn import close_btn
from bot.keyboards.inline.button import AdminCallback
from bot.keyboards.inline.admin_btn import channel_settings


@dp.callback_query(AdminCallback.filter(F.action == "mandatory_membership"), IsAdmin())
async def channel_setting(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id
        mid = call.message.message_id
        language_code = call.from_user.language_code 
        btn = close_btn()  # Inline button to close the message
    
        if AM(user_id=user_id, feature='mandatory_membership'):
            if user_id == ADMIN:
                # Retrieve all channels if the admin is the main ADMIN
                data = db.select_channels()
            else:
                # Retrieve channels added by the current admin
                data = MMM.channels(initiator_user_id=user_id)

            if not data:
                # If no channels are found, indicate that the list is empty
                text = translator(text="❔ The channel list is empty!\n\n", dest=language_code)
            else:
                # Construct a message listing the channels
                text = translator(text="🔰 List of channels:\n\n", dest=language_code)
                count = 0
                for x in data:
                    try:
                        count += 1
                        chat_id = str(-100) + str(x['channel_id'])  # Telegram channel ID
                        channel = await bot.get_chat(chat_id=chat_id)  # Get channel details
                        text += (f"<b><i>{count}</i>. Name:</b> <i>{channel.full_name}</i>\n"
                                 f"<b>Username:</b> <i>@{channel.username}\n</i>"
                                 f"<b>Added date:</b> <i>{x['created_at']}\n</i>"
                                 f"<b>Added by user_id:</b> <i>{x['initiator_user_id']}\n\n</i>")
                    except Exception as err:
                        root_logger.error(err)  # Log any errors in retrieving channel details
            btn = channel_settings(language_code=language_code)  # Button for channel settings
        else:
            # Inform the admin that they do not have the necessary permissions
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=mid,
            text=f'<b><i>{text}</i></b>',
            reply_markup=btn  # Update the message with a translated response and appropriate buttons
        )

        await state.update_data({"message_id": call.message.message_id})  # Save the message ID in the FSM context
    except Exception as err:
        logging.error(err)  # Log any exceptions that occur

