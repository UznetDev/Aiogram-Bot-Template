import logging


class SafeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'chat_id'):
            record.chat_id = None
        if not hasattr(record, 'language_code'):
            record.language_code = 'N/A'
        if not hasattr(record, 'execution_time'):
            record.execution_time = 0.0
        return super().format(record)
