import logging


logger = logging.getLogger(__name__)


class OneTimeFilter(logging.Filter):
    def __init__(self, name=""):
        self.messages = set()
        super().__init__(name)

    def filter(self, record):
        if record.msg in self.messages:
            return False
        self.messages.add(record.msg)
        return True

