import datetime
import re
import socket
import traceback


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

        Returns:
            [str]: The string without color bits
        """
        # remove all color bits
        text = re.sub(r"§[0-9a-fk-or]*", "", text).replace("|", "")
        if trim:
            text = text.strip()
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
