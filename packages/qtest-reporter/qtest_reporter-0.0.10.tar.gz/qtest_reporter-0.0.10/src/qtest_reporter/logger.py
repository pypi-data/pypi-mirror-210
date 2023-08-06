"""This module provides Logger class for simple logging usage"""
import logging


logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
    )


class Logger:
    """Main logger class"""
    def __init__(self) -> None:
        self._logger = logging.getLogger()
