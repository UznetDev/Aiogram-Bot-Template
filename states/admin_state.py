from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    send_ads = State()
    add_channel = State()
    add_admin = State()
    check_user = State()
    send_message_to_user = State()
