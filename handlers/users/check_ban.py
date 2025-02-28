import logging
from loader import dp, bot, db
from aiogram import types
from function.translator import translator
from keyboards.inline.close_btn import close_btn
from data.config import yil_oy_kun, soat_minut_sekund, ADMIN
from filters.ban import IsBan

@dp.message(IsBan())
async def ban_handler(msg: types.Message):
    """
    Handles incoming messages from banned users. Sends a message informing them of their ban status and provides
    contact information for admins. Adds the user to the database if they are not already present.

    Args:
        msg (types.Message): The incoming message from the user.

    Returns:
        None
    """
    try:
        # Get the user's language code and ID
        lang = msg.from_user.language_code
        user_id = msg.from_user.id

        # Check if the user is banned and retrieve ban information
        info = db.check_user_ban(user_id=user_id)

        # Retrieve admin information
        text = translator(text="🛑 You are banned!:\n"
                        "⚠ If you think this is a mistake, contact the admin.",
                    dest=lang)
        if info['initiator_user_id'] == 1 or info['initiator_user_id'] == 0:
            text += f"\n\n<b>👮‍♂️ Admin: Bot</b>\n "

        else:
            admin_info = await bot.get_chat(chat_id=info['updater_user_id'])
            text += f"\n\n<b>👮‍♂️ Admin @{admin_info.username}</b>\n "
        if info['comment'] is not None:
            text += f"<b>📝 Comment: {info['comment']}</b>\n"

        admins = await bot.get_chat(chat_id=ADMIN)

        # Create the response message

        text += f'<b>👩‍💻 Super admin @{admins.username}</b>\n'

        # Send the response message to the user
        await msg.answer(text=f"<b>{text}</b>", reply_markup=close_btn())

        # Add the user to the database if they are not already present
        if db.check_user(user_id=user_id) is None:
            db.insert_user(user_id=user_id,
                           date=f"{yil_oy_kun} / {soat_minut_sekund}")

    except Exception as err:
        logging.error(f"Error in start_handler: {err}")
