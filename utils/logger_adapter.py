import logging


class ChatLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Ensure 'extra' exists in kwargs
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        # Update 'extra' with adapter's extra
        kwargs['extra'].update(self.extra)
        return msg, kwargs
