"""The utils package which contains database, finder, logger, players, and text
"""

import pymongo

from .database import Database
from .finder import Finder
from .logger import Logger
from .players import Players
from .server import Server
from .text import Text


class utils:
    """A class to hold all the utils classes"""

    def __init__(
        self,
        col: pymongo.collection.Collection,
        logger: Logger = None,
        debug=True,
        allowJoin=False,
        level: int = 20,
    ):
        """Initializes the utils class

        Args:
            logger (Logger): The logger class
            col (pymongo.collection.Collection): The database collection
            debug (bool, optional): Show debugging. Defaults to True.
            level (int, optional): The logging level. Defaults to 20 (INFO).
        """
        self.col = col
        self.logLevel = level
        self.logger = (
            logger
            if logger
            else Logger(debug, level=self.logLevel, allowJoin=allowJoin)
        )
        self.logger.clear()
        self.text = Text(self.logger)
        if allowJoin:
            self.server = Server(self.logger)
        else:
            self.server = None
        self.database = Database()

        self.players = Players(
            logger=self.logger, col=self.col, server=self.server)
        self.finder = Finder(
            logger=self.logger, col=self.col, Text=self.text, Player=self.players
        )
