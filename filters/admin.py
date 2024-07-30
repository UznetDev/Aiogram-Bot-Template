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
        self.cid = message.from_user.id
        self.dada = db.select_admin(cid=self.cid)
        if self.cid == ADMIN:
            return True
        elif self.dada is not None:
            return True
        else:
            return False


class SelectAdmin:
    """
    Class to handle various admin-related actions.

    Attributes:
        cid (int): The user ID.
        super_admin (int): The ID of the super admin.
        dada (list): The admin details from the database.
    """

    def __init__(self, cid):
        self.cid = cid
        self.super_admin = ADMIN
        self.dada = db.select_admin(cid=self.cid)

    def send_message(self) -> bool:
        """
        Checks if the user has permission to send messages.

        Returns:
            bool: True if the user can send messages, False otherwise.
        """
        if self.cid == self.super_admin:
            return True
        elif self.dada[3] == 1:
            return True
        else:
            return False

    def view_statistika(self) -> bool:
        """
        Checks if the user has permission to view statistics.

        Returns:
            bool: True if the user can view statistics, False otherwise.
        """
        if self.cid == self.super_admin:
            return True
        elif self.dada[4] == 1:
            return True
        else:
            return False

    def download_statistika(self) -> bool:
        """
        Checks if the user has permission to download statistics.

        Returns:
            bool: True if the user can download statistics, False otherwise.
        """
        if self.cid == self.super_admin:
            return True
        elif self.dada[5] == 1:
            return True
        else:
            return False

    def block_user(self) -> bool:
        """
        Checks if the user has permission to block other users.

        Returns:
            bool: True if the user can block users, False otherwise.
        """
        if self.cid == self.super_admin:
            return True
        elif self.dada[6] == 1:
            return True
        else:
            return False

    def channel_settings(self) -> bool:
        """
        Checks if the user has permission to change channel settings.

        Returns:
            bool: True if the user can change channel settings, False otherwise.
        """
        if self.cid == self.super_admin:
            return True
        elif self.dada[7] == 1:
            return True
        else:
            return False

    def add_admin(self) -> bool:
        """
        Checks if the user has permission to add new admins.

        Returns:
            bool: True if the user can add new admins, False otherwise.
        """
        if self.cid == self.super_admin:
            return True
        elif self.dada[8] == 1:
            return True
        else:
            return False

