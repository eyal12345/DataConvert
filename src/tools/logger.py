from src.tools.singleton import Singleton
import logging

class Logger(metaclass=Singleton):

    # constructor
    def __init__(self, log_path):
        self.logger = logging.getLogger(log_path)
        self.logger.setLevel(logging.DEBUG)
