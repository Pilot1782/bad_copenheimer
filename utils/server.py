import os
import time

from javascript import On, require


class Server:
    """Class to allow for joining a server"""

    def __init__(self, logger):
        # clear nmp cache
        os.remove("%appdata%/.minecraft/nmp-cache/") if os.path.exists(
            "%appdata%/.minecraft/nmp-cache/"
        ) else None

        self.ip = None
        self.port = 25565
        self.mineflayer = require("mineflayer")
        self.pathfinder = require("mineflayer-pathfinder")
        self.username = None
        self.logger = logger
        self.STATE = "NOT_CONNECTED"

    def start(self, ip, port, username):
        """Join the server"""
        # clear nmp cache
        os.remove("%appdata%/.minecraft/nmp-cache/") if os.path.exists(
            "%appdata%/.minecraft/nmp-cache/"
        ) else None

        self.ip = ip
        self.port = port
        self.username = username

        # server info
        self.names = []
        self.position = None
        self.heldItem = "nothing"

        # create the bot
        self.bot = self.mineflayer.createBot(
            {
                "host": self.ip,
                "port": self.port,
                "username": self.username,
                "auth": "microsoft",
            }
        )

        time.sleep(2)

        # check if the bot is connected an account
        log = self.logger.read()
        if "To sign in, use a web browser to open the page" in log:
            self.logger.print("Authenticating...")

            # find that last instance of the string
            lines = log.splitlines()
            for line in lines[::-1]:
                if "To sign in, use a web browser to open the page" in line:
                    # get the code
                    line = line.split(
                        "To sign in, use a web browser to open the page https://www.microsoft.com/link and enter the code "
                    )[1]
                    line = line.split(" to authenticate.")[0]
                    self.STATE = "AUTHENTICATING:" + line
                    break
        else:
            self.STATE = "CONNECTING"
            self.logger.print("Authenticated!")

        @On(self.bot, "spawn")
        def handle(*args):
            self.STATE = "CONNECTED"

            players = self.bot.players
            self.heldItem = (
                self.bot.heldItem.name if self.bot.heldItem is not None else "nothing"
            )
            self.logger.info("I spawned 👋")
            self.logger.info("I am at {}".format(self.bot.entity.position))
            self.logger.info("I am with {}".format(players))
            self.logger.info("I am holding a(n) {}".format(self.heldItem))

            for player in players:  # append lower case names to list
                self.names.append(player.lower())

            self.position = (
                round(self.bot.entity.position.x, 2),
                round(self.bot.entity.position.y, 2),
                round(self.bot.entity.position.z, 2),
            )

            self.inventory = []
            for item in self.bot.inventory.items():
                self.inventory.append(item)

        @On(self.bot, "end")
        def handle(*args):
            self.logger.info("Bot ended!")
            self.STATE = "DISCONNECTED:WHITELISTED"

        @On(self.bot, "error")
        def handle(*args):
            text = args if len(args) < 100 else args[:100]
            self.logger.error("Bot errored!{} ".format(args))
            self.STATE = "ERROR"

        @On(self.bot, "disconnected")
        def handle(*args):
            self.logger.error("Bot disconnected! {}".format(args))
            self.STATE = "DISCONNECTED:ERROR"

        @On(self.bot, "kicked")
        def handle(*args):
            self.logger.error("Bot kicked! {}".format(args))
            self.STATE = "DISCONNECTED:KICKED"

    def getPlayers(self):
        return self.names

    def getState(self):
        return self.STATE

    def getInfo(self):
        return {
            "names": self.names,
            "position": self.position,
            "heldItem": self.heldItem,
            "state": self.STATE,
        }
