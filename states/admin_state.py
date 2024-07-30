from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
    """
    This class defines a set of states for the Admin's workflow in the bot.

    It uses the StatesGroup from aiogram's finite state machine (FSM) module to manage
    different stages of interaction with the admin. Each state represents a step
    in the process that the bot can handle during its interaction with the admin.
    """

    send_ads = State()
    """
    State for sending advertisements. In this state, the admin can provide the 
    content for advertisements that will be sent to users.

    Parameters:
    - None

    Returns:
    - None
    """

    add_channel = State()
    """
    State for adding a new channel. In this state, the admin will provide details 
    about the new channel to be added.

    Parameters:
    - None

    Returns:
    - None
    """

    add_admin = State()
    """
    State for adding a new admin. In this state, the admin will provide information 
    necessary to add a new admin to the system.

    Parameters:
    - None

    Returns:
    - None
    """

    check_user = State()
    """
    State for checking user information. In this state, the admin can query or 
    review details about a specific user.

    Parameters:
    - None

    Returns:
    - None
    """

    send_message_to_user = State()
    """
    State for sending a message to a user. In this state, the admin will specify 
    the message content and the recipient user.

    Parameters:
    - None

    Returns:
    - None
    """
