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
        cid = msg.from_user.id

        # Check if the user is banned and retrieve ban information
        info = db.check_user_ban(cid=cid)
        logging.info(f"User ban info: {info}")

        # Retrieve admin information
        admin_info = await bot.get_chat(chat_id=info[2])
        admins = await bot.get_chat(chat_id=ADMIN)

        # Create the response message
        text = translator(text="🛑 You are banned!:\n"
                               "⚠ If you think this is a mistake, contact the admin.",
                          dest=lang)
        text += f'\n\n<b>👮‍♂️ Admin @{admin_info.username}</b>\n <b>👩‍💻 Super admin @{admins.username}</b>\n'

        # Send the response message to the user
        await msg.answer(text=f"<b>{text}</b>", reply_markup=close_btn())

        # Add the user to the database if they are not already present
        if db.check_user(cid=cid) is None:
            db.add_user(cid=cid,
                        date=f"{yil_oy_kun} / {soat_minut_sekund}")

    except Exception as err:
        logging.error(f"Error in start_handler: {err}")
