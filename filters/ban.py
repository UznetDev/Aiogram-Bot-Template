import logging
from aiogram.filters import BaseFilter
from aiogram.types import Message
from data.config import ADMIN
from loader import db


class IsBan(BaseFilter):
    """
    Filter to check if the user is banned.

    Attributes:
        super_admin (int): The ID of the super admin.
    """

    def __init__(self):
        self.super_admin = ADMIN

    async def __call__(self, message: Message) -> bool:
        """
        Checks if the message sender is banned.

        Args:
            message (Message): The message object from the user.

        Returns:
            bool: True if the user is banned, False otherwise.
        """
        try:
            self.cid = message.from_user.id
            self.dada = db.select_admin(cid=self.cid)
            check_ban = db.check_user_ban(cid=self.cid)

            # If the user is the super admin, they are not banned
            if self.cid == self.super_admin:
                return False
            # If the user is an admin, they are not banned
            elif self.dada is not None:
                return False
            # If there is no ban record for the user, they are not banned
            elif check_ban is None:
                return False
            # If the user is found in the ban list, they are banned
            else:
                return True
        except Exception as err:
            # Log any exceptions that occur and return False
            logging.error(err)
            return False
