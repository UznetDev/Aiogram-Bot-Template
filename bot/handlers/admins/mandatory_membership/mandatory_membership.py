import logging
from loader import dp, bot, db
from aiogram import types, F
from keyboards.inline.button import AdminCallback
from keyboards.inline.admin_btn import channel_settings
from keyboards.inline.close_btn import close_btn
from filters.admin import IsAdmin, SelectAdmin
from aiogram.fsm.context import FSMContext
from api.translator import translator


@dp.callback_query(AdminCallback.filter(F.action == "mandatory_membership"), IsAdmin())
async def mandatory_membership(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id  # The ID of the admin who initiated the action
        mid = call.message.message_id  # The ID of the message to be updated
        language_code = call.from_user.language_code  # The language_codeuage code for translation
        data = SelectAdmin(user_id=user_id)  # Check if the user has admin permissions
        btn = close_btn()  # Create a button for closing the message

        if data.channel_settings():
            # Read the current setting for mandatory membership from the database
            mandatory_membership = db.select_setting('mandatory_membership')
            if mandatory_membership == 'True':
                # If mandatory membership is enabled, disable it
                text = translator(text='☑️ Forced membership disabled!', dest=language_code)
                nex_mandatory_membership = 'False'
            else:
                # If mandatory membership is disabled, enable it
                text = translator(text='✅ Mandatory membership enabled!', dest=language_code)
                nex_mandatory_membership = 'True'

            # Update the database with the new membership status
            db.update_settings_key(updater_user_id=user_id, key='mandatory_membership', value=nex_mandatory_membership)
            btn = channel_settings(language_code=language_code)  # Update the button to reflect the new settings
        else:
            text = translator(text='❌ Unfortunately, you do not have this right!', dest=language_code)

        # Edit the message with the new status and close button
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=mid,
                                    text=f'<b><i>{text}</i></b>',
                                    reply_markup=btn)
        # Update FSM state with the current message ID
        await state.update_data({
            "message_id": call.message.message_id
        })
    except Exception as err:
        # Log any errors that occur during the execution
        logging.error(err)
