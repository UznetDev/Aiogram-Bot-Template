import logging
from .button import MainCallback
from aiogram.utils.keyboard import InlineKeyboardBuilder


def close_btn():
    try:
        # Create an instance of InlineKeyboardBuilder to build the keyboard
        btn = InlineKeyboardBuilder()

        # Add a button to the keyboard with the text "❌ Close"
        btn.button(
            text='❌ Close',
            callback_data=MainCallback(action="close", q="").pack()  # Define the callback data
        )

        # Adjust the keyboard layout to ensure the button is displayed correctly
        btn.adjust(1)

        # Return the markup for the keyboard
        return btn.as_markup()

    except Exception as err:
        # Log any exceptions that occur during the process
        logging.error(err)
        return False
