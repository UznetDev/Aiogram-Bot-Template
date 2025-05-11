import logging
import hashlib

def x_or_y(data):
    """
    Converts a boolean-like value to a corresponding emoji string representation.

    Parameters:
    - data: The value to be converted. It can be of any type that can be evaluated as a boolean.

    Returns:
    - '✅' if the input data evaluates to True.
    - '❌' if the input data evaluates to False.
    - '' (an empty string) if an exception occurs during the evaluation or conversion.

    Functionality:
    - The function first attempts to convert the input `data` to a boolean.
    - Depending on the boolean value, it returns a corresponding checkmark ('✅') or cross mark ('❌') emoji.
    - If an error occurs during the conversion (e.g., due to invalid input), it logs the error and returns an empty string.

    Error Handling:
    - Logs any exceptions encountered during the conversion of `data` to a boolean value.
    """
    try:
        data = bool(data)  # Convert data to a boolean value
        if data:
            return '✅'  # Return checkmark if data is True
        else:
            return '❌'  # Return cross mark if data is False
    except Exception as err:
        logging.error(err)  # Log the error
        return ''


def format_seconds(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours} soat {minutes} daqiqa {seconds} soniya"


def to_hash(text: str) -> int:
    hex16 = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return int(hex16, 16) 