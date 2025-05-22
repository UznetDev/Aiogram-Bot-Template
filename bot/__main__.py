
import os
import sys
import asyncio
import logging
from .main import main
from bot.data.config import log_file_name
from bot.loader import root_logger, log_file_name, formatter


if __name__ == "__main__":

    if not os.path.exists('logs'):
        os.mkdir('logs')

    if not os.path.exists(log_file_name):
        with open(log_file_name, 'w') as f:
            pass
        
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    

    asyncio.run(main())
