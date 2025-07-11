import logging

class RawTextMemory:
    def __init__(self):
        self.logs = []
        self.logger = logging.getLogger("RawText")

    def log(self, msg):
        self.logger.info(msg)
        self.logs.append(msg)
