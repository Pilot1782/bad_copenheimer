
import time
import traceback
from typing import List, Union, Optional, Dict
import interactions
import mcstatus
import pymongo
import requests


class Players:
    """Class to hold all the player related functions"""

    def __init__(self, logger, col: pymongo.collection.Collection, text, server=None):
        """Initializes the Players class

        Args:
            logger (Logger): The logger class
            col (pymongo.collection.Collection): The database collection
        """
        self.logger = logger
        self.server = server
        self.col = col
        self.text = text

    def crackCheckAPI(self, host: str, port: str = "25565") -> bool:
        """Checks if a server is cracked using the mcstatus.io API

        Args:
            host (str): the host of the server
            port (str, optional): port of the server. Defaults to "25565".

        Returns:
            bool: True if the server is cracked, False if not
        """
        url = "https://api.mcstatus.io/v2/status/java/" + \
            host + ":" + str(port)

        resp = requests.get(url)
        if resp.status_code == 200:
            self.logger.debug("Server is cracked")
            return resp.json()["eula_blocked"]
        else:
            return False

    def crackedPlayerList(
        self, host: str, port: str = "25565", username: str = "pilot1782"
    ) -> Union[List[str], bool]:
        """Gets a list of players on a server

        Args:
            host (str): the host of the server
            port (str, optional): the port of the server. Defaults to "25565".
            username (str, optional): Username to join with. Defaults to "pilot1782".

        Returns:
            list[str] | False: A list of players on the server, or False if the server is not cracked
        """
        self.logger.info("Getting player list for ip: " + host + ":" + port)

        import chat as chat2

        args = [host, "--port", port, "--offline-name", username]
        tStart = time.time()
        try:
            chat2.main(args)
        except Exception:
            self.logger.error(traceback.format_exc())
            return [] if self.crackCheckAPI(host, port) else False

        while True:
            if time.time() - tStart > 5:
                break
            if len(chat2.playerArr) > 0:
                chat2.playerArr.remove(username.lower())
                return chat2.playerArr
            time.sleep(0.2)

        out = [] if self.crackCheckAPI(host, port) else False

        lines = self.logger.read().split("\n")
        lines = lines[::-1]
        flag = False
        for line in lines:
            if "kick" in line.lower():
                flag = not flag
            if "Getting player list for ip: " + host in line and flag:
                return []

            if "PlayerListProtocol{" + host in line:
                self.logger.info(host + " is an online mode server")
                return False

        return out

    def playerHead(self, name: str) -> Optional[interactions.File]:
        """Downloads a player head from minotar.net

        Args:
            name (str): player name

        Returns:
            interactions.file | None: file object of the player head
        """
        url = "https://minotar.net/avatar/" + name
        r = requests.get(url)
        with open("playerhead.png", "wb") as f:
            f.write(r.content)
        self.logger.debug("Player head downloaded")
        return interactions.File(filename="playerhead.png")

    def playerList(self, host: str, port: int = 25565, usrname: str = "") -> List[Dict]:
        """Return a list of players on a Minecraft server

        Args:
            host (str): The hostname/ip of the server
            port (int, optional): port of the server. Defaults to 25565.

        Returns:
            list[dict]: list of players in the form of:
                [
                    {
                        "name": "playername",
                        "uuid": "playeruuid"
                    }
                ]
        """

        if self.col is None:
            self.logger.print("Collection not set")
            return []

        # generate all the player lists

        # Database list
        res = self.col.find_one({"host": host})
        DBplayers = res["lastOnlinePlayersList"] if res is not None else []
        DBnames = [p["name"] for p in DBplayers]

        # cracked server list
        cpNames = self.crackedPlayerList(host, str(port))
        cpNames = [] if cpNames is False else cpNames

        # normal server list
        normal = []
        try:
            self.logger.info("Getting player list from server")
            server = mcstatus.JavaServer.lookup(host + ":" + str(port))
            status = server.status()
            if status.players.sample is not None:
                normal = [
                    {"name": self.text.cFilter(p.name, True), "uuid": p.id}
                    for p in status.players.sample
                ]
        except TimeoutError:
            self.logger.error("Timeout error")
            normal = []
        except ConnectionRefusedError:
            self.logger.error("Connection refused")
            normal = []
        except Exception:
            self.logger.error(traceback.format_exc())
            normal = []

        smapleNames = [p["name"] for p in normal]

        # combine all the names fetched from the server
        onlineNames = cpNames + smapleNames

        # remove duplicates
        onlineNames = list(dict.fromkeys(onlineNames))
        # clean the names
        for name in onlineNames:
            name = self.text.cFilter(name, True)

        players = []
        for name in DBnames:
            online = name in onlineNames

            # get uuid
            url = "https://api.mojang.com/users/profiles/minecraft/" + name
            uuid = "---n/a---"
            res = requests.get(url)
            if "error" not in res.text.lower():
                uuid = res.json()["id"]

            players.append({"name": name, "uuid": uuid, "online": online})

        # check if any players are missing from the database
        for name in onlineNames:
            if name not in DBnames:
                url = "https://api.mojang.com/users/profiles/minecraft/" + name
                uuid = "---n/a---"
                res = requests.get(url)
                if "error" not in res.text.lower():
                    uuid = res.json()["id"]
                players.append({"name": name, "uuid": uuid, "online": True})

        # update the database
        self.col.update_one(
            {"host": host},
            {"$set": {"lastOnlinePlayersList": players}},
            upsert=True,
        )
        self.logger.info(
            f"Updated player list for {host} ({len(players)} players): {players}"
        )

        return DBplayers
