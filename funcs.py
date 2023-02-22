# pyright: reportGeneralTypeIssues=false

import base64
import random
import re
import subprocess
import datetime
import time
import os
import traceback
import requests
import sys
import socket
import logging
import pymongo

import interactions
from mcstatus import JavaServer
import mcstatus

norm = sys.stdout


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

    def read(self):
        with open("log.log", "r") as f:
            return f.read()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
    filename="log.log",
    filemode="a",
)
log = logging.getLogger("STDOUT")
out = StreamToLogger(log, logging.INFO)
sys.stdout = out
sys.stderr = StreamToLogger(log, logging.ERROR)


class funcs:
    """Cursed code that I don't want to touch. It works, but it's not pretty.
    # STOP HERE

    Beyond this point is code unmaintained and at risk of mabye being important.
    Once this file was made, no proper docs on the methods have been made except those that I sometimes remember.

    """

    def __init__(
        self,
        collection=None,  # pyright: ignore[reportGeneralTypeIssues]
        path: str = os.path.dirname(os.path.abspath(__file__)),
        debug: bool = True,
    ):
        """Init the class

        Args:
            path (str, optional): Path to the directory of the folder. Defaults to os.path.dirname(os.path.abspath(__file__)).
        """

        self.stdout = out
        self.path = path + ("\\" if os.name == "nt" else "/")
        self.col = collection
        self.settings_path = self.path + (
            r"\settings.json" if os.name == "nt" else "/settings.json"
        )
        self.debug = debug

        # clear log.log
        with open(self.path + "log.log", "w") as f:
            f.write("")

    # ------------------ #
    # Functions getting defeined

    def ptime(self) -> str:
        """Get the current time in a readable format

        Returns:
            str: time in format: year month/day hour:minute:second
        """
        x = time.localtime()
        z = []
        for i in x:
            z.append(str(i))
        y = ":".join(z)
        z = f"{z[0]} {z[1]}/{z[2]} {z[3]}:{z[4]}:{z[5]}"
        return z
    
    def timeNow(self) -> str:
        """Get the current time in a readable format

        Returns:
            str: time in format: year-month-day hour:minute:second
        """
        return datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=0))  # no clue why this is needed but it works now?
        ).strftime("%Y-%m-%d %H:%M:%S")

    # Run a command and get line by line output
    def run_command(self, command: str, powershell: bool = False) -> str:
        """Just a better os.system

        Args:
            command (raw string): desired command
            powershell (bool, optional): use powershell for windows. Defaults to False.

        Returns:
            string: error message

        Yields:
            string: console output of command
        """

        if powershell:
            command = rf"C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe -command {command}"
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        # Read stdout from subprocess until the buffer is empty !
        for line in iter(p.stdout.readline, b""):  # type: ignore
            if line:  # Don't print blank lines
                yield line
        # This ensures the process has completed, AND sets the 'returncode' attr
        while p.poll() is None:
            time.sleep(0.1)  # Don't waste CPU-cycles
        # Empty STDERR buffer
        err = p.stderr.read()  # type: ignore
        if p.returncode != 0:
            # The run_command() function is responsible for logging STDERR
            self.dprint(str(err))
            return "Error: " + str(err)

    # Print but for debugging
    def dprint(self, *text, override: bool = False, end="\n"):
        """Prints a message to the console and the log file

        Args:
            override (bool, optional): Force print to the console regardless of debugging. Defaults to False.
            end (str, optional): end of the string. Defaults to "\n".
        """
        print(" ".join((str(i) for i in text)), end=end)

        if self.debug or override:
            sys.stdout = norm  # reset stdout
            print(" ".join((str(i) for i in text)))
            sys.stdout = self.stdout  # redirect stdout

    def print(self, *args, **kwargs) -> None:
        """Prints a message to the console"""
        self.dprint(" ".join(map(str, args)), **kwargs, override=True)

    def check(self, host: str, port: str = "25565", webhook: str = "") -> dict | None:
        """Checks out a host and adds it to the database if it's not there

        Args:
            host (String): ip of the server

        Returns:
            dict: {
                        "host":"ipv4 addr",
                        "lastOnline":"unicode time",
                        "lastOnlinePlayers": int,
                        "lastOnlineVersion":"Name Version",
                        "lastOnlineDescription":"Very Good Server",
                        "lastOnlinePing":"unicode time",
                        "lastOnlinePlayersList":["Notch","Jeb"],
                        "lastOnlinePlayersMax": int,
                        "cracked": bool,
                        "lastOnlineFavicon":"base64 encoded image"
                    }
            | None: if the server is offline
        """

        if self.col is None:
            self.dprint("Collection is None")
            return None
        
        hostname = self.resolveHost(host)
        ip = self.resolveIP(host)
        
        # check the ip and hostname to make sure they arr vaild as a mc server
        try:
            server = mcstatus.JavaServer.lookup(ip + ":" + str(port))
            status = server.status()
        except BrokenPipeError:
            ip = host
        except ConnectionRefusedError:
            ip = host
        except OSError:
            ip = host
        except Exception:
            ip = host
        
        try:
            server = mcstatus.JavaServer.lookup(hostname + ":" + str(port))
            status = server.status()
        except BrokenPipeError:
            ip = host
        except ConnectionRefusedError:
            ip = host
        except OSError:
            ip = host
        except Exception:
            ip = host
        

        try:
            server = mcstatus.JavaServer.lookup(host + ":" + str(port))
            try:
                status = server.status()
            except BrokenPipeError:
                return None
            except ConnectionRefusedError:
                return None
            except OSError:
                return None

            self.dprint("Checking hostname/ip")
            cpLST = self.crackedPlayerList(host, str(port))  # cracked player list
            cracked = bool(cpLST or cpLST == [])

            self.dprint("Getting players")
            players = []
            try:
                if status.players.sample is not None:
                    self.dprint("Getting players from sample")

                    for player in list(
                        status.players.sample
                    ):  # pyright: ignore [reportOptionalIterable]
                        url = f"https://api.mojang.com/users/profiles/minecraft/{player.name}"
                        jsonResp = requests.get(url)
                        if len(jsonResp.text) > 2:
                            jsonResp = jsonResp.json()

                            if jsonResp:
                                players.append(
                                    {
                                        "name": self.cFilter(
                                            jsonResp["name"]
                                        ).lower(),  # pyright: ignore [reportGeneralTypeIssues]
                                        "uuid": jsonResp["id"],
                                    }
                                )
                        else:
                            uuid = "---n/a---"
                            if "id" in str(jsonResp.text):
                                uuid = jsonResp.json()["id"]
                            players.append(
                                {
                                    "name": self.cFilter(player.name).lower(),
                                    "uuid": uuid,
                                }
                            )
                elif cracked:
                    self.dprint("Getting players from cracked player list")
                    playerlst = cpLST

                    for player in playerlst:
                        jsonResp = requests.get(
                            "https://api.mojang.com/users/profiles/minecraft/" + player
                        )
                        uuid = "---n/a---"
                        if "id" in str(jsonResp.text):
                            uuid = jsonResp.json()["id"]
                        players.append(
                            {
                                "name": self.cFilter(player).lower(),
                                "uuid": uuid,
                            }
                        )
            except Exception:
                self.dprint("Error getting player list", traceback.format_exc())

            # remove duplicates from player list
            players = [i for n, i in enumerate(players) if i not in players[n + 1 :]]

            data = {
                "host": ip,
                "hostname": hostname,
                "lastOnline": time.time(),
                "lastOnlinePlayers": status.players.online,
                "lastOnlineVersion": self.cFilter(
                    str(re.sub(r"§\S*[|]*\s*", "", status.version.name))
                ),
                "lastOnlineDescription": self.cFilter(str(status.description)),
                "lastOnlinePing": int(status.latency * 10),
                "lastOnlinePlayersList": players,
                "lastOnlinePlayersMax": status.players.max,
                "lastOnlineVersionProtocol": self.cFilter(str(status.version.protocol)),
                "cracked": cracked,
                "whitelisted": self.isWhitelisted(ip, int(port)),
                "favicon": status.favicon,
            }

            if not self.col.find_one({"host": host}):
                self.print("{} not in database, adding...".format(host))
                self.col.insert_one(data)
                if webhook != "":
                    requests.post(
                        webhook,
                        json={"content": f"New server added to database: {host}"},
                    )

            for i in list(self.col.find_one({"host": host})["lastOnlinePlayersList"]):
                try:
                    if i not in data["lastOnlinePlayersList"]:
                        if type(i) == str:
                            url = f"https://api.mojang.com/users/profiles/minecraft/{i}"
                            jsonResp = requests.get(url)
                            if len(jsonResp.text) > 2:
                                jsonResp = jsonResp.json()

                                if jsonResp is not None:
                                    data["lastOnlinePlayersList"].append(
                                        {
                                            "name": self.cFilter(jsonResp["name"]),
                                            "uuid": jsonResp["id"],
                                        }
                                    )
                        else:
                            data["lastOnlinePlayersList"].append(i)
                except Exception:
                    self.print(
                        traceback.format_exc(),
                        " --\\/-- ",
                        host,  # pyright: ignore [reportInvalidStringEscapeSequence]
                    )
                    break

            self.col.update_one({"host": host}, {"$set": data})

            return data
        except TimeoutError:
            self.dprint("Timeout Error")
            return None
        except Exception:
            self.print(traceback.format_exc(), " | ", host)
            return None

    def remove_duplicates(self) -> None:
        """Removes duplicate entries from the database

        Returns:
            None
        """
        if self.col is None:
            return
        field = "host"
        cursor = self.col.find({})
        seen = set()
        for doc in cursor:
            value = doc[field]
            if value in seen:
                self.col.delete_one({"_id": doc["_id"]})
            else:
                seen.add(value)

    def verify(self, search: dict, serverList: list):
        """Verifies a search

        Args:
            search [dict], len > 0: {
                "host":"ipv4 addr",
                "lastOnline":"unicode time",
                "lastOnlinePlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePing":"unicode time",
                "lastOnlinePlayersList":["Notch","Jeb"],
                "lastOnlinePlayersMax": int,
                "favicon":"base64 encoded image"
            }
            serverList [list], len > 0: {
                "host":"ipv4 addr", # optional
                "lastOnline":"unicode time", # optional
                "lastOnlinePlayers": int, # optional
                "lastOnlineVersion":"Name Version", # optional
                "lastOnlineDescription":"Very Good Server", # optional
                "lastOnlinePing":"unicode time", # optional
                "lastOnlinePlayersList":["Notch","Jeb"], # optional
                "lastOnlinePlayersMax": int, # optional
                "favicon":"base64 encoded image" # optional
            }

        Returns:
            [list]: {
                "host":"ipv4 addr",
                "lastOnline":"unicode time",
                "lastOnlinePlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePing":"unicode time",
                "lastOnlinePlayersList":["Notch","Jeb"],
                "lastOnlinePlayersMax": int,
                "favicon":"base64 encoded image"
            }
        """
        out = []
        _items = list(search.items())
        for server in serverList:
            flag = True
            for _item in _items:
                key = str(_item[0])
                value = str(_item[1])
                if key in server:
                    if str(value).lower() not in str(server[key]).lower():
                        flag = False
                        break
            if flag:
                out.append(server)

        self.print(str(len(out)) + " servers match")

        random.shuffle(out)
        return out

    def _find(self, search: dict) -> list:
        """Finds a server in the database

        Args:
            search [dict], len > 0: {
                "host":"ipv4 addr",
                "lastOnlineMaxPlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePlayersList": ["WIP", "WIP"],
            }

        Returns:
            [dict]: {
                "host":"ipv4 addr",
                "lastOnline":"unicode time",
                "lastOnlinePlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePing":"unicode time",
            }
        """
        if self.col is None:
            return []

        # find the server given the parameters
        if search == {}:
            return [
                {
                    "host": "Server not found",
                    "lastOnline": 0,
                    "lastOnlinePlayers": -1,
                    "lastOnlineVersion": "Server not found",
                    "lastOnlineDescription": "Server not found",
                    "lastOnlinePing": -1,
                    "lastOnlinePlayersList": [],
                    "lastOnlinePlayersMax": -1,
                    "favicon": "Server not found",
                }
            ]

        search_query = {}
        for key, value in search.items():
            if isinstance(value, str):
                search_query[key] = {"$regex": f"^{value}$", "$options": "i"}
            else:
                search_query[key] = value
        return list(self.col.find(search_query))

    def genEmbed(self, _serverList: list[dict], _port: str = "25565"):
        """Generates an embed for the server list

        Args:
            serverList [list]: {
                "host":"ipv4 addr",
                "lastOnline":"unicode time",
                "lastOnlinePlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePing":"unicode time",
                "lastOnlinePlayersList":["Notch","Jeb"],
                "lastOnlinePlayersMax": int,
                "favicon":"base64 encoded image"
            }

        Returns:
            [
                [interactions.Embed]: The embed,
                _file: favicon file,
                button: interaction button,
            ]
        """

        if len(_serverList) == 0 or self.col is None:
            embed = interactions.Embed(
                title="No servers found",
                description="No servers found",
                color=0xFF0000,
                timestamp=self.timeNow(),
            )
            buttons = [
                interactions.Button(
                    label="Show Players",
                    custom_id="show_players",
                    style=interactions.ButtonStyle.PRIMARY,
                    disabled=True,
                ),
                interactions.Button(
                    label="Next Server",
                    custom_id="rand_select",
                    style=interactions.ButtonStyle.PRIMARY,
                    disabled=True,
                ),
            ]

            row = interactions.ActionRow(components=buttons)

            return [embed, None, row]

        random.shuffle(_serverList)
        info = _serverList[0]

        if info is None:
            logging.error("Server not found: " + str(_serverList))

            self.dprint("Server not found", len(_serverList))
            embed = interactions.Embed(
                title="Server not found",
                description="Server not found",
                color=0xFF0000,
            )
            buttons = [
                interactions.Button(
                    label="Show Players",
                    custom_id="show_players",
                    style=interactions.ButtonStyle.PRIMARY,
                    disabled=True,
                ),
                interactions.Button(
                    label="Next Server",
                    custom_id="rand_select",
                    style=interactions.ButtonStyle.PRIMARY,
                    disabled=True,
                ),
            ]

            row = interactions.ActionRow(
                components=buttons  # pyright: ignore [reportGeneralTypeIssues]
            )

            return [embed, None, row, info]

        info2 = self.check(info["host"], _port)
        if info2 is not None:
            info = info2

        numServers = len(_serverList)
        online = info is not None

        try:
            _serverList.pop(0)
        except IndexError:
            pass

        # setup the embed
        embed = interactions.Embed(
            title=(("🟢 "if not info["whitelisted"] else "🟠 ") if online else "🔴 ") + info["host"],
            description="Host name: `"+info["hostname"]+"`\n```\n" + info["lastOnlineDescription"] + "```",
            timestamp=self.timeNow(),
            color=(0x00FF00 if online else 0xFF0000),
            type="rich",
            fields=[
                interactions.EmbedField(
                    name="Players",
                    value=f"{info['lastOnlinePlayers']}/{info['lastOnlinePlayersMax']}",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Version", value=info["lastOnlineVersion"], inline=True
                ),
                interactions.EmbedField(
                    name="Ping", value=str(info["lastOnlinePing"]), inline=True
                ),
                interactions.EmbedField(
                    name="Cracked", value=f"{info['cracked']}", inline=True
                ),
                interactions.EmbedField(
                    name="Whitelisted", value=f"{info['whitelisted']}", inline=True
                ),
                interactions.EmbedField(
                    name="Last Online",
                    value=(
                        time.strftime(
                            "%Y/%m/%d %H:%M:%S", time.localtime(info["lastOnline"])
                        )
                    )
                    if info["host"] != "Server not found."
                    else "0/0/0 0:0:0",
                    inline=True,
                ),
            ],
            footer=interactions.EmbedFooter(
                text="Server ID: "
                + (
                    str(self.col.find_one({"host": info["host"]})["_id"])
                    if info["host"] != "Server not found."
                    else "-1"
                )
                + "\nOut of {} servers".format(numServers)
            ),  # pyright: ignore [reportOptionalSubscript]
        )

        try:  # this adds the favicon in the most overcomplicated way possible
            if online:
                stats = info

                fav = (
                    stats["favicon"]
                    if "favicon" in str(stats) and stats is not None
                    else None
                )
                if fav is not None:
                    bits = fav.split(",")[1]

                    with open("server-icon.png", "wb") as f:
                        f.write(base64.b64decode(bits))
                    _file = interactions.File(filename="server-icon.png")
                    embed.set_thumbnail(url="attachment://server-icon.png")

                    self.print("Favicon added")
                else:
                    _file = None
            else:
                _file = None
        except Exception:
            self.print(traceback.format_exc(), info)
            _file = None

        players = info
        if players is not None:
            players = (
                players["lastOnlinePlayersList"]
                if "lastOnlinePlayersList" in players
                else []
            )
        else:
            players = []

        buttons = [
            interactions.Button(
                label="Show Players",
                custom_id="show_players",
                style=interactions.ButtonStyle.PRIMARY,
                disabled=(
                    len(players) == 0 or not online or info["lastOnlinePlayers"] == 0
                ),
            ),
            interactions.Button(
                label="Next Server",
                custom_id="rand_select",
                style=interactions.ButtonStyle.PRIMARY,
                disabled=(len(_serverList) == 0),
            ),
        ]

        row = interactions.ActionRow(
            components=buttons  # pyright: ignore [reportGeneralTypeIssues]
        )

        return embed, _file, row

    def cFilter(self, text: str, trim: bool = True):
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

    def crackCheckAPI(self, host: str, port: str = "25565") -> bool:
        """Checks if a server is cracked using the mcstatus.io API

        Args:
            host (str): the host of the server
            port (str, optional): port of the server. Defaults to "25565".

        Returns:
            bool: True if the server is cracked, False if not
        """
        url = "https://api.mcstatus.io/v2/status/java/" + host + ":" + str(port)

        resp = requests.get(url)
        if resp.status_code == 200:
            self.print("Fetching from API")
            return resp.json()["eula_blocked"]
        else:
            return False

    def crackedPlayerList(
        self, host: str, port: str = "25565", username: str = "pilot1782"
    ) -> list[str] | bool:
        """Gets a list of players on a server

        Args:
            host (str): the host of the server
            port (str, optional): the port of the server. Defaults to "25565".
            username (str, optional): Username to join with. Defaults to "pilot1782".

        Returns:
            list[str] | False: A list of players on the server, or False if the server is not cracked
        """
        import chat as chat2

        args = [host, "--port", port, "--offline-name", username]
        tStart = time.time()
        try:
            chat2.main(args)
        except Exception:
            self.print(traceback.format_exc())
            return [] if self.crackCheckAPI(host, port) else False

        while True:
            if time.time() - tStart > 15:
                break
            if len(chat2.playerArr) > 0:
                chat2.playerArr.remove(username.lower())
                return chat2.playerArr
            time.sleep(0.2)

        out = [] if self.crackCheckAPI(host, port) else False

        if "kicked: this server has mods that require" in self.stdout.read().lower():
            self.dprint("Server has mods, assuming not cracked")
            out = False if out is False else True

        return out

    def playerHead(self, name: str) -> interactions.File | None:
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
        self.dprint("Player head downloaded")
        return interactions.File(filename="playerhead.png")

    def get_sorted_versions(
        self, collection: pymongo.collection.Collection
    ) -> list[dict[str, int]]:
        """I have no idea how this works, but it does, thanks github copilot

        Args:
            collection (pymongo.collection.Collection): server collection

        Returns:
            list[dict[str, int]]: sorted list of versions by frequency
        """
        pipeline = [
            {"$match": {"lastOnlineVersion": {"$exists": True}}},
            {"$group": {"_id": "$lastOnlineVersion", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        result = list(collection.aggregate(pipeline))
        result = [{"version": r["_id"], "count": r["count"]} for r in result]
        return result

    def get_total_players_online(
        self, collection: pymongo.collection.Collection
    ) -> int:
        """Gets the total number of players online across all servers via ai voodoo

        Args:
            collection (pymongo.collection.Collection): server collection

        Returns:
            int: total number of players online
        """
        pipeline = [
            {"$match": {"lastOnlinePlayers": {"$gte": 1, "$lt": 100000}}},
            {"$group": {"_id": None, "total_players": {"$sum": "$lastOnlinePlayers"}}},
        ]
        result = list(collection.aggregate(pipeline))
        if len(result) > 0:
            return result[0]["total_players"]
        else:
            return 0
        
    def resolveHost(self, ip: str) -> str:
        """Resolves a hostname to an IP address into a hostname

        Args:
            host (str): hostname

        Returns:
            str: IP address
        """
        # test if the ip is an ip address
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
            self.print("Not an IP address")
            return ip
        
        try:
            host = socket.gethostbyaddr(ip)[0]
            # if the hostname is an ip address, return the original ip
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
                self.print("Hostname is an IP address")
                return ip
            else:
                # check the host is a valid hostname by checking if it has a dot and ping it
                if "." in host:
                    if os.name == "nt":
                        self.dprint("Host: " + host)
                        
                        # try pinging the ip first
                        if subprocess.run(["ping", "-n", "1", ip], capture_output=True).returncode == 0:
                            self.dprint("The host is online")
                            # try pinging the hostname
                            ping = subprocess.run(["ping", "-n", "1", host], capture_output=True)
                            if ping.returncode == 1:
                                self.dprint("Hostname is offline")
                            
                            return host if ping.returncode == 0 else ip
                        else:
                            self.dprint("The host is offline")
                            return ip
                    else:
                        self.dprint("Host: " + host)
                        
                        # try pinging the ip first
                        if subprocess.run(["ping", "-c", "1", ip], capture_output=True).returncode == 0:
                            self.dprint("The host is online")
                            # try pinging the hostname
                            ping = subprocess.run(["ping", "-c", "1", host], capture_output=True)
                            if ping.returncode == 1:
                                self.dprint("Hostname is offline")
                            
                            return host if ping.returncode == 0 else ip
                        else:
                            self.dprint("The host is offline")
                            return ip
                else:
                    self.print("Invalid hostname")
                    return ip
        except socket.herror:
            self.print("Hostname not found")
            return ip
        except Exception:
            self.print(traceback.format_exc())
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
            self.print("Hostname not found")
            return host
        except Exception:
            self.print(traceback.format_exc())
            return host
        
    def isWhitelisted(self, ip: str, port: int) -> bool:
        """
        Check if a given Minecraft server is whitelisted.

        Args:
            ip (str): IP address of the Minecraft server.
            port (int): Port number of the Minecraft server.

        Returns:
            bool: True if the server is whitelisted, False otherwise.
        """
        # connect to the server
        try:
            sock = socket.create_connection((ip, port), timeout=5)
            sock.send(b"\xfe\x01")
            data = sock.recv(1024)
            sock.close()
        except:
            return False

        try:
            # check if the server is whitelisted
            if data[3] == 0:
                return True
            else:
                return False
        except:
            # assume the server is not whitelisted
            return False




if __name__ == "__main__":
    sys.stdout = norm
    print("Bruh what are you doing here?\nThis is a library, not a script bro.")
