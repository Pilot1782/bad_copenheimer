import datetime
import re
import socket
import traceback
import unicodedata


class Text:
    def __init__(self, logger):
        """Initializes the text class

        Args:
            logger (Logger): The logger class
        """
        self.logger = logger

    def cFilter(self, text: str, trim: bool = True) -> str:
        """Removes all color bits from a string

        Args:
            text [str]: The string to remove color bits from
            trim [bool]: Whether to trim the string or not

        Returns:
            [str]: The string without color bits
        """
        # remove all color bits
        text = re.sub(r"§[0-9a-fk-or]*", "", text).replace("|", "")
        if trim:
            text = text.strip()
        
        text = text.replace("@", "@ ")  # fix @ mentions
        return text

    def markFilter(self, text: str) -> str:
        """Changes color tags to those that work with markdown

        Args:
            text (str): text to change

        Returns:
            str: text with markdown color tags
        """

        # color char prefix \u001b[{color}m
        # color #s
        # 30: Gray   <- §7
        # 31: Red    <- §c
        # 32: Green  <- §a
        # 33: Yellow <- §e
        # 34: Blue   <- §9
        # 35: Pink   <- §d
        # 36: Cyan   <- §b
        # 37: White  <- §f

        # use the ansi color codes
        text = self.colorAnsi(text)

        return "```ansi\n" + text + "\n```"

    def colorAnsi(self, text: str) -> str:
        # 30: Gray   <- §7
        # 31: Red    <- §c
        # 32: Green  <- §a
        # 33: Yellow <- §e
        # 34: Blue   <- §9
        # 35: Pink   <- §d
        # 36: Cyan   <- §b
        # 37: White  <- §f
        colorChar = ""  # \u001b
        ansi = {
            "§0": colorChar + "[30m",
            "§1": colorChar + "[34m",
            "§2": colorChar + "[32m",
            "§3": colorChar + "[36m",
            "§4": colorChar + "[31m",
            "§5": colorChar + "[35m",
            "§6": colorChar + "[33m",
            "§7": colorChar + "[30m",
            "§9": colorChar + "[34m",
            "§a": colorChar + "[32m",
            "§b": colorChar + "[36m",
            "§c": colorChar + "[31m",
            "§d": colorChar + "[35m",
            "§e": colorChar + "[33m",
            "§f": colorChar + "[37m",
            "§l": "",
            "§k": "",
            "§m": "",
            "§n": "",
            "§o": "",
            "§r": "",
        }

        for color in ansi:
            text = text.replace(color, ansi[color])

        # remove remaining color codes
        text = re.sub(r"§[0-9a-fk-or]*", "", text)

        return text

    def resolveHost(self, ip: str) -> str:
        """Resolves a hostname into a hostname

        Args:
            host (str): hostname

        Returns:
            str: IP address
        """
        # test if the ip is an ip address
        if not ip.replace(".", "").isnumeric():
            self.logger.info("Not an IP address")
            return ip

        if ip == "127.0.0.1":
            return ip

        try:
            host = socket.gethostbyaddr(ip)

            # test if the host is online
            if host[0] == "":
                self.logger.info("Host is offline")
                return ip

            return host[0]
        except socket.herror:
            self.logger.info("IP address not found")
            return ip

    def resolveIP(self, host: str) -> str:
        """Resolves a hostname to an IP address

        Args:
            host (str): hostname

        Returns:
            str: IP address
        """
        try:
            ip = socket.gethostbyname(host)
            return ip
        except socket.gaierror:
            self.logger.info("Hostname not found")
            return host
        except Exception:
            self.logger.error(traceback.format_exc())
            return host

    def timeNow(self):
        # return local time
        return datetime.datetime.now(
            datetime.timezone(
                datetime.timedelta(
                    hours=0
                )  # no clue why this is needed but it works now?
            )
        ).strftime("%Y-%m-%d %H:%M:%S")
