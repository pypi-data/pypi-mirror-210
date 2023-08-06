"""
Logger module
"""

import logging
import datetime
from colorama import Fore, Style


class Logger:
    def __init__(self, name: str):
        """
        A logger for PySync that can print messages to the console and/or to a file
        :param name: The name of the logger
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

    def logger_method(self, message: str, color: str = Fore.GREEN):
        """
        Method to log
        :param message: message for log
        :param color: color for message in console
        """
        box_width = len(message) + 2
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        if not self.logger.handlers:
            box_formatter = logging.Formatter('%(message)s')
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(box_formatter)
            self.logger.addHandler(console_handler)

        self.logger.info(color + "+" + "-" * box_width + "+")
        self.logger.info(color + "|" + " " * ((box_width - len(message)) // 2) + message + " " * (
                    (box_width - len(message) + 1) // 2) + "|")
        self.logger.info(color + "|" + " " * ((box_width - len(timestamp)) // 2) + timestamp + " " * (
                    (box_width - len(timestamp) + 1) // 2) + "|")
        self.logger.info(color + "+" + "-" * box_width + "+" + Style.RESET_ALL)
