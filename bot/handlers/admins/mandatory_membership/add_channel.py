from aiogram import types, F
from aiogram.fsm.context import FSMContext


from bot.filters.admin import IsAdmin
from bot.states.admin_state import AdminState
from bot.keyboards.inline.close_btn import close_btn
from bot.keyboards.inline.button import AdminCallback
from bot.loader import dp, bot, root_logger, AM, translator


@dp.callback_query(AdminCallback.filter(F.action == "add_channel"), IsAdmin())
async def add_channel(call: types.CallbackQuery, state: FSMContext):
    try:
        user_id = call.from_user.id  # The ID of the admin initiating the action
        mid = call.message.message_id  # The ID of the message triggering the callback
        language_code = call.from_user.language_code  # The language_codeuage code of the admin for message translation
        btn = close_btn()  # Inline button to close the message

        if AM(user_id=user_id, feature='mandatory_membership'):
            # If the admin is authorized, prompt for the channel ID
            await state.set_state(AdminState.add_channel)  # Set the FSM state for adding a channel
            text = translator(text="😊 Please send the channel id...", dest=language_code)
            await state.update_data({"message_id": call.message.message_id})  # Save the message ID in the FSM context
        else:
            # Inform the admin that they do not have the necessary permissions
            text = translator(text="❌ Unfortunately, you do not have this right!", dest=language_code)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=mid,
            text=f'{text}',
            reply_markup=btn  # Update the message with a translated response
        )
        await state.update_data({"message_id": call.message.message_id})  # Save the message ID in the FSM context
    except Exception as err:
        root_logger.error(err)  # Log any exceptions that occur
