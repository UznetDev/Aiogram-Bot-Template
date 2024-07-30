import logging, os
from loader import bot
from data.config import ADMIN, log_file_name
from keyboards.inline.close_btn import close_btn
from aiogram import types


async def on_startup_notify():
    """
    Sends a startup notification to the admin and optionally sends a log file.

    This asynchronous function is intended to be run during the bot's startup process.
    It performs two main actions:
    1. Sends a notification message to the admin with bot startup information and a special command.
    2. Checks if a log file exists and is not empty, and if so, sends it to the admin.
       If the log file exceeds a certain size, it will be deleted after sending.

    Parameters:
    - None

    Returns:
    - None

    Steps:
    1. **Send Startup Notification**:
       - Uses `bot.send_message` to send a message to the admin.
       - The message includes bot startup confirmation, a link to the admin panel,
         and a special command for the admin.

    2. **Send Log File** (if applicable):
       - Checks if the log file specified by `log_file_name` exists and is not empty.
       - If it is valid, uses `bot.send_document` to send the log file to the admin with a caption.
       - Checks the size of the log file and deletes it if it exceeds a certain threshold (40 MB in this case).

    Exceptions:
    - Catches and logs any exceptions that occur during the execution of the function using the `logging` module.
      - Logs errors that occur during sending the message or handling the log file.
      - Logs any exceptions that occur during the entire process.

    This function does not take any parameters and does not return any value. It is designed to
    perform actions related to bot startup notifications and log file management.
    """
    try:
        # Send startup notification to the admin
        await bot.send_message(chat_id=ADMIN,
                               text="<b>Bot ishga tushdi!\n</b>"
                                    "<b>Admin panelni ochish /admin\n</b>"
                                    "<i>Maxsus faqat siz uchun /stat buyrug'i</i>",
                               reply_markup=close_btn())

        try:
            # Check if the log file exists and is not empty
            if os.path.exists(log_file_name) and os.path.getsize(log_file_name):
                try:
                    # Create a file object for the log file
                    document = types.input_file.FSInputFile(path=log_file_name)

                    # Send the log file to the admin
                    await bot.send_document(chat_id=ADMIN,
                                            document=document,
                                            caption=f'<b>Update log</b>')

                    # Delete the log file if it exceeds 40 MB
                    if (os.path.getsize(log_file_name)) * (1024 * 124) > 40:
                        os.remove(log_file_name)
                except Exception as err:
                    # Log any errors that occur while sending the log file
                    logging.error(err)
        except Exception as Err:
            # Log any errors that occur while checking the log file
            logging.exception(Err)

    except Exception as err:
        # Log any errors that occur while sending the startup notification
        logging.error(err)
