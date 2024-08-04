# import logging
# from aiogram import BaseMiddleware
# from loader import bot, db, DB
# from data.config import ADMIN
# from aiogram.filters import BaseFilter
# from aiogram.types import Message, CallbackQuery
#
#
# class User_Check(BaseFilter, BaseMiddleware):
#     """
#     Middleware and filter class to check if a user is a member of required channels.
#
#     This class combines the functionality of a filter and middleware to ensure that users
#     are members of specified channels before they can access certain bot features.
#     """
#
#     def __init__(self):
#         """
#         Initializes the User_Check class.
#
#         Parameters:
#         - None
#
#         This constructor sets up the ADMIN variable from the configuration.
#         """
#         self.ADMIN = ADMIN
#
#     async def __call__(self, message: Message, call=CallbackQuery) -> bool:
#         """
#         Checks if the user is a member of required channels.
#
#         Parameters:
#         - message (Message): The incoming message object. This is used to obtain user information.
#         - call (CallbackQuery): The incoming callback query object. This is used if the message object is not available.
#
#         Returns:
#         - bool: Returns True if the user is not a member of the required channels and False otherwise.
#
#         This method:
#         - Reads the database to check if channel membership verification is required.
#         - If required, verifies the user's membership status in each specified channel.
#         - Logs errors if any exceptions occur during the check.
#         """
#         try:
#             # Retrieve the channel membership check requirement from the database
#             data = DB.reading_db()
#             if data['join_channel']:
#                 try:
#                     # Try to get the user ID from the message object
#                     cid = message.from_user.id
#                 except Exception as err:
#                     # If message object is not available, use callback query object
#                     cid = call.from_user.id
#                     logging.error(err)
#
#                 # If the user is not the admin, perform the channel check
#                 if cid != self.ADMIN:
#                     force = False
#                     result = db.select_channels()
#                     for x in result:
#                         try:
#                             # Construct the chat ID for the channel
#                             ids = str(-100) + str(x[1])
#                             await bot.get_chat(ids)
#                             try:
#                                 # Check the user's membership status in the channel
#                                 res = await bot.get_chat_member(chat_id=ids, user_id=cid)
#                             except:
#                                 # Continue if unable to retrieve chat member information
#                                 continue
#                             # If the user is not a member, administrator, or creator, set force to True
#                             if res.status == 'member' or res.status == 'administrator' or res.status == 'creator':
#                                 pass
#                             else:
#                                 force = True
#                         except Exception as err:
#                             logging.error(err)
#                     return force
#                 else:
#                     return False
#             else:
#                 return False
#         except Exception as err:
#             logging.error(err)
#
#         return False

