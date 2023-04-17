import os
import time

from javascript import On, require


class Server:
    """Class to allow for joining a server"""

    def __init__(self, logger):
        self.ip = None
        self.port = 25565
        self.mineflayer = require("mineflayer")
        self.pathfinder = require("mineflayer-pathfinder")
        self.username = None
        self.logger = logger
        self.STATE = "NOT_CONNECTED"

        # clear nmp cache
        self.clearNMPCache()

    def start(self, ip, port, username):
        """Join the server"""
        # clear nmp cache
        self.clearNMPCache()

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

    def clearNMPCache(self):
        """Clear the nmp cache"""

        # check that the cache exists
        if os.name == "nt":
            minecraftPath = os.path.expandvars(r"%appdata%\.minecraft\nmp-cache")
            if not os.path.exists(minecraftPath):
                return
        elif os.name == "posix":
            if not os.path.exists("~/.minecraft/nmp-cache/"):
                return

        if os.getpid() == 0:  # if running as root
            if os.name == "nt":  # windows
                minecraftPath = os.path.expandvars(r"%appdata%\.minecraft\nmp-cache")
                if os.path.exists(minecraftPath):
                    os.remove(minecraftPath)
                else:
                    self.logger.print("No cache to delete")
            elif os.name == "posix":  # linux
                os.remove("~/.minecraft/nmp-cache/") if os.path.exists(
                    "~/.minecraft/nmp-cache/"
                ) else self.logger.print("No cache to delete")
            else:
                self.logger.error("Unknown OS")
        else:
            self.logger.print("Clearing cache as root...")
            if os.name == "nt":
                os.system(
                    'powershell.exe "Start-Process -Verb runas -FilePath cmd.exe -ArgumentList \\"/c, rmdir /s /q %appdata%\\.minecraft\\nmp-cache\\""'
                )
            elif os.name == "posix":
                os.system("sudo rm -rf ~/.minecraft/nmp-cache/")
            else:
                self.logger.error("Unknown OS")
