from aiogram.filters import BaseFilter
from aiogram.types import Message
from data.config import ADMIN
from loader import db


class IsSuperAdmin(BaseFilter):
    """
    Filter to check if the user is a super admin.

    Attributes:
        ADMIN (int): The ID of the super admin.
    """

    def __init__(self):
        self.ADMIN = ADMIN

    async def __call__(self, message: Message) -> bool:
        """
        Checks if the message sender is the super admin.

        Args:
            message (Message): The message object from the user.

        Returns:
            bool: True if the user is the super admin, False otherwise.
        """
        user_id = message.from_user.id
        if user_id == self.ADMIN:
            return True
        else:
            return False


class IsAdmin(BaseFilter):
    """
    Filter to check if the user is an admin or the super admin.

    Attributes:
        ADMIN (int): The ID of the super admin.
    """

    def __init__(self):
        self.ADMIN = ADMIN

    async def __call__(self, message: Message) -> bool:
        """
        Checks if the message sender is an admin or the super admin.

        Args:
            message (Message): The message object from the user.

        Returns:
            bool: True if the user is an admin or the super admin, False otherwise.
        """
        self.user_id = message.from_user.id
        self.dada = db.select_admin(user_id=self.user_id)
        if self.user_id == ADMIN:
            return True
        elif self.dada is not None:
            return True
        else:
            return False


class SelectAdmin:
    """
    Class to handle various admin-related actions.

    Attributes:
        user_id (int): The user ID.
        super_admin (int): The ID of the super admin.
        dada (list): The admin details from the database.
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.super_admin = ADMIN
        self.dada = db.select_admin(user_id=self.user_id)

    def send_message(self) -> bool:
        """
        Checks if the user has permission to send messages.

        Returns:
            bool: True if the user can send messages, False otherwise.
        """
        if self.user_id == self.super_admin:
            return True
        elif self.dada['send_message'] == 1:
            return True
        else:
            return False

    def view_statistika(self) -> bool:
        """
        Checks if the user has permission to view statistics.

        Returns:
            bool: True if the user can view statistics, False otherwise.
        """
        if self.user_id == self.super_admin:
            return True
        elif self.dada['statistika'] == 1:
            return True
        else:
            return False

    def download_statistika(self) -> bool:
        """
        Checks if the user has permission to download statistics.

        Returns:
            bool: True if the user can download statistics, False otherwise.
        """
        if self.user_id == self.super_admin:
            return True
        elif self.dada['download_statistika'] == 1:
            return True
        else:
            return False

    def block_user(self) -> bool:
        """
        Checks if the user has permission to block other users.

        Returns:
            bool: True if the user can block users, False otherwise.
        """
        if self.user_id == self.super_admin:
            return True
        elif self.dada['block_user'] == 1:
            return True
        else:
            return False

    def channel_settings(self) -> bool:
        """
        Checks if the user has permission to change channel settings.

        Returns:
            bool: True if the user can change channel settings, False otherwise.
        """
        if self.user_id == self.super_admin:
            return True
        elif self.dada['channel_settings'] == 1:
            return True
        else:
            return False

    def add_admin(self) -> bool:
        """
        Checks if the user has permission to add new admins.

        Returns:
            bool: True if the user can add new admins, False otherwise.
        """
        if self.user_id == self.super_admin:
            return True
        elif self.dada['add_admin'] == 1:
            return True
        else:
            return False


    def set_data(self) -> bool:
        """
        Checks if the user has permission to set data.
        Returns:
           bool: True if the user can set data, False otherwise.
           """
        if self.user_id == self.super_admin:
            return True
        elif self.dada['set_data'] == 1:
            return True
        else:
            return False
        
        
    def get_data(self) -> bool:
        """
        Checks if the user has permission to get data.
        Returns:
           bool: True if the user can get data, False otherwise.
           """
        if self.user_id == self.super_admin:
            return True
        elif self.dada['get_data'] == 1:
            return True
        else:
            return False