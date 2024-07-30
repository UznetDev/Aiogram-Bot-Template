import logging
from loader import dp
from aiogram import types
from keyboards.inline.button import AdminCallback
from keyboards.inline.close_btn import close_btn
from aiogram import F
from aiogram.fsm.context import FSMContext
from states.admin_state import AdminState
from filters.admin import SelectAdmin, IsAdmin
from function.translator import translator


@dp.callback_query(AdminCallback.filter(F.action == "send_advertisement"), IsAdmin())
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the initiation of the advertisement sending process.

    This function:
    - Checks if the user has the necessary permissions to send advertisements.
    - Updates the state to allow for the advertisement sending process.
    - Provides feedback to the user about the status of the operation.

    Args:
        call (types.CallbackQuery): The callback query object that triggered this handler.
        state (FSMContext): The finite state machine context for managing state data.

    Raises:
        Exception: Logs any errors encountered during the process.

    Returns:
        None
    """
    try:
        user_id = call.from_user.id
        message_id = call.message.message_id
        language = call.from_user.language_code
        is_admin = SelectAdmin(cid=user_id)

        if is_admin.send_message():
            # Set the state to `AdminState.send_ads` to handle advertisement sending.
            await state.set_state(AdminState.send_ads)

            # Inform the admin that the system is ready to receive the advertisement.
            text = translator(
                text="Send the advertisement...",
                dest=language
            )

            # Update state data to include the current message ID.
            await state.update_data({"message_id": call.message.message_id})
        else:
            # Inform the admin that they do not have the necessary permissions.
            text = translator(
                text="❌ Unfortunately, you do not have this permission!",
                dest=language
            )

        # Edit the callback message to provide feedback and close the interaction.
        await call.message.edit_text(
            text=f'<b><i>{text}</i></b>',
            reply_markup=close_btn()
        )

        # Update the state with the current message ID.
        await state.update_data({"message_id": message_id})

    except Exception as err:
        # Log any exceptions encountered.
        logging.error(err)


