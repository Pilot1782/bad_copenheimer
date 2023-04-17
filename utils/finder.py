import base64
import re
import threading
import time
import traceback
from json import JSONDecodeError
from typing import List, Dict, Optional

import interactions
import mcstatus
import pymongo
import requests


class ServerType:
    def __init__(self, host: str, protocol: int, joinability: str = "unknown"):
        self.host = host
        self.protocol = protocol
        self.joinability = joinability

    def __str__(self):
        return f"ServerType({self.host}, {self.protocol}, {self.joinability})"


class Finder:
    def __init__(
        self,
        col: pymongo.collection.Collection,
        logger,
        Text,
        Player,
    ) -> None:
        """Initializes the Finder class

        Args:
            col (pymongo.collection.Collection): The database collection
            logger (_type_): The logger class
            Text (_type_): The text class
        """
        self.col = col
        self.logger = logger
        self.Text = Text
        self.Player = Player

    def check(
        self, host: str, port: str = "25565", webhook: str = "", *args
    ) -> Optional[Dict]:
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
            self.logger.debug("Collection is None")
            return None

        self.logger.debug("Checking " + str(host))

        # check for embeded port
        if ":" in host:
            host = host.split(":")
            port = host[1]
            host = host[0]

        hostname = self.Text.resolveHost(host)
        ip = self.Text.resolveIP(host)

        # check if the host is online
        try:
            mcstatus.JavaServer.lookup(host + ":" + str(port)).status()
        except Exception:
            self.logger.debug("Server is offline")
            return None

        # check the ip and hostname to make sure they arr vaild as a mc server
        try:
            server = mcstatus.JavaServer.lookup(ip + ":" + str(port))
            status = server.status()
        except Exception:
            ip = host
        try:
            server = mcstatus.JavaServer.lookup(hostname + ":" + str(port))
            status = server.status()
        except Exception:
            hostname = host

        joinability = self.join(host, port, "Pilot1782").joinability
        cracked = bool(joinability == "CRACKED")

        try:
            server = mcstatus.JavaServer.lookup(host + ":" + str(port))
            status = server.status()

            cpLST = self.Player.crackedPlayerList(
                host, str(port)
            )  # cracked player list
            cracked = bool(
                (cpLST is not None and type(cpLST) is not bool) or cracked)

            self.logger.debug("Getting players")
            players = []
            try:
                if status.players.sample is not None:
                    self.logger.debug("Getting players from sample")

                    for player in list(
                        status.players.sample
                    ):  # pyright: ignore [reportOptionalIterable]
                        url = f"https://api.mojang.com/users/profiles/minecraft/{player.name}"
                        jsonResp = requests.get(url)
                        if len(jsonResp.text) > 2:
                            try:
                                jsonResp = jsonResp.json()

                                if jsonResp and "id" in jsonResp:
                                    players.append(
                                        {
                                            "name": self.Text.cFilter(
                                                jsonResp["name"]
                                            ).lower(),  # pyright: ignore [reportGeneralTypeIssues]
                                            "uuid": jsonResp["id"],
                                        }
                                    )
                                else:
                                    joinability = "CRACKED"
                            except JSONDecodeError:
                                self.logger.print(
                                    "Error getting player list, bad json response"
                                )
                                self.logger.error(
                                    f"Error getting player list, bad json response: {jsonResp}"
                                )
                                continue
                            except KeyError:
                                self.logger.print(
                                    "Error getting player list, bad json response"
                                )
                                self.logger.error(
                                    f"Error getting player list, bad json response: {jsonResp}"
                                )
                                continue
                        else:
                            uuid = "---n/a---"
                            if "id" in str(jsonResp.text):
                                uuid = jsonResp.json()["id"]
                            players.append(
                                {
                                    "name": self.Text.cFilter(player.name).lower(),
                                    "uuid": uuid,
                                }
                            )
                elif cracked:
                    self.logger.debug(
                        "Getting players from cracked player list")
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
                                "name": self.Text.cFilter(player).lower(),
                                "uuid": uuid,
                            }
                        )
            except Exception:
                self.logger.print("Error getting player list",
                                  traceback.format_exc())
                self.logger.error(traceback.format_exc())

            # remove duplicates from player list
            players = [i for n, i in enumerate(
                players) if i not in players[n + 1:]]

            cracked = bool(joinability == "CRACKED")

            data = {
                "host": ip,
                "hostname": hostname,
                "lastOnline": time.time(),
                "lastOnlinePlayers": status.players.online,
                "lastOnlineVersion": self.Text.cFilter(
                    str(re.sub(r"§\S*[|]*\s*", "", status.version.name))
                ),
                "lastOnlineDescription": self.Text.cFilter(str(status.description)),
                "lastOnlinePing": int(status.latency * 10),
                "lastOnlinePlayersList": players,
                "lastOnlinePlayersMax": status.players.max,
                "lastOnlineVersionProtocol": self.Text.cFilter(
                    str(status.version.protocol)
                ),
                "cracked": cracked,
                "whitelisted": joinability == "WHITELISTED",
                "favicon": status.favicon,
            }

            if not self.col.find_one({"host": ip}) and not self.col.find_one(
                {"hostname": hostname}
            ):
                self.print("{} not in database, adding...".format(host))
                self.col.update_one(
                    {"host": ip},
                    {"$set": data},
                    upsert=True,
                )
                if webhook != "":
                    requests.post(
                        webhook,
                        json={"content": f"New server added to database: {host}"},
                    )
            else:  # update current values with database values
                dbVal = self.col.find_one({"host": ip})
                if dbVal is not None:
                    data["whitelisted"] = (
                        (dbVal["whitelisted"] or data["whitelisted"])
                        if "whitelisted" in dbVal
                        else data["whitelisted"]
                    )
                    data["cracked"] = dbVal["cracked"] or data["cracked"]
                    data["hostname"] = (
                        (
                            data["hostname"]
                            if not data["hostname"].replace(".", "").isdigit()
                            else dbVal["hostname"]
                        )
                        if "hostname" in dbVal
                        else data["hostname"]
                    )

                    for i in dbVal["lastOnlinePlayersList"]:
                        try:
                            if i not in data["lastOnlinePlayersList"]:
                                if type(i) is str:
                                    url = f"https://api.mojang.com/users/profiles/minecraft/{i}"
                                    jsonResp = requests.get(url)
                                    if len(jsonResp.text) > 2:
                                        jsonResp = jsonResp.json()

                                        if jsonResp is not None:
                                            data["lastOnlinePlayersList"].append(
                                                {
                                                    "name": self.Text.cFilter(
                                                        jsonResp["name"]
                                                    ),
                                                    "uuid": jsonResp["id"],
                                                }
                                            )
                                else:
                                    data["lastOnlinePlayersList"].append(i)
                        except Exception:
                            self.print(
                                traceback.format_exc(),
                                " --\\/-- ",
                                host,
                            )
                            self.logger.error(traceback.format_exc())
                            break

            self.col.update_one({"host": ip}, {"$set": data}, upsert=True)

            return data
        except TimeoutError:
            self.logger.debug("Timeout Error")
            return None
        except Exception:
            self.logger.error(traceback.format_exc())
            return None

    def get_doc_at_index(
        self,
        col: pymongo.collection.Collection,
        pipeline: list,
        index: int = 0,
    ) -> Optional[dict]:
        try:
            newPipeline = pipeline.copy()

            if type(newPipeline) is dict:
                newPipeline = [newPipeline]

            newPipeline.append({"$skip": index})
            newPipeline.append({"$limit": 1})
            newPipeline.append({"$project": {"_id": 1}})
            newPipeline.append({"$limit": 1})
            newPipeline.append({"$addFields": {"doc": "$$ROOT"}})
            newPipeline.append({"$project": {"_id": 0, "doc": 1}})

            result = col.aggregate(newPipeline, allowDiskUse=True)
            try:
                return col.find_one(next(result)["doc"])
            except StopIteration:
                self.logger.error("Index out of range")
                return None
        except:
            self.logger.error(traceback.format_exc())
            self.logger.error(
                "Error getting document at index: {}".format(pipeline))
            return None

    def genEmbed(
        self,
        search: dict,
        index: int = 0,
        numServ: int = 0,
        allowJoin: bool = False,
    ) -> list:
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

        if numServ == 0 or self.col is None:
            embed = interactions.Embed(
                title="No servers found",
                description="No servers found",
                color=0xFF0000,
                timestamp=self.Text.timeNow(),
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
                interactions.Button(
                    label="Join",
                    custom_id="join",
                    style=interactions.ButtonStyle.PRIMARY,
                    disabled=True,
                ),
            ]

            row = interactions.ActionRow(components=buttons)

            return [embed, None, row]

        info = self.get_doc_at_index(self.col, search, index)

        if info is None:
            self.logger.error("Iterating too far")
            info = self.get_doc_at_index(self.col, search, 0)
            if info is None:
                self.logger.error("No servers found")
                embed = interactions.Embed(
                    title="No servers found",
                    description="No servers found",
                    color=0xFF0000,
                    timestamp=self.Text.timeNow(),
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
                    interactions.Button(
                        label="Join",
                        custom_id="join",
                        style=interactions.ButtonStyle.PRIMARY,
                        disabled=True,
                    ),
                ]

                row = interactions.ActionRow(components=buttons)

                return [embed, None, row]

        online = False
        try:
            server = mcstatus.JavaServer.lookup(info["host"])
            online = True
            status = server.status()
            online = True
            
            # update the online player count
            info["lastOnlinePlayers"] = status.players.online
        except:
            self.logger.debug("Server offline", info["host"])

        hostname = info["hostname"] if "hostname" in info else info["host"]
        whitelisted = info["whitelisted"] if "whitelisted" in info else False

        # setup the embed
        embed = interactions.Embed(
            title=(("🟢 " if not whitelisted else "🟠 ") if online else "🔴 ")
            + info["host"],
            description="Host name: `"
            + hostname
            + "`\n```\n"
            + str(info["lastOnlineDescription"])
            .encode("unicode_escape")
            .decode("utf-8")
            .replace("\\n", "\n")
            + "```",
            timestamp=self.Text.timeNow(),
            color=(0x00FF00 if online else 0xFF0000),
            type="rich",
            fields=[
                interactions.EmbedField(
                    name="Players",
                    value=f"{info['lastOnlinePlayers']}/{info['lastOnlinePlayersMax']}",
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Version",
                    value=f'{info["lastOnlineVersion"]}'.encode(
                        "unicode_escape"
                    ).decode("utf-8"),
                    inline=True,
                ),
                interactions.EmbedField(
                    name="Ping", value=str(info["lastOnlinePing"]), inline=True
                ),
                interactions.EmbedField(
                    name="Cracked", value=f"{info['cracked']}", inline=True
                ),
                interactions.EmbedField(
                    name="Whitelisted", value=f"{whitelisted}", inline=True
                ),
                interactions.EmbedField(
                    name="Last Online",
                    value=(
                        time.strftime(
                            "%Y/%m/%d %H:%M:%S", time.localtime(
                                info["lastOnline"])
                        )
                        if not online
                        else time.strftime(  # give the last online time if the server is offline
                            "%Y/%m/%d %H:%M:%S", time.localtime(time.time())
                        )
                        if not online
                        else time.strftime(  # give the last online time if the server is offline
                            "%Y/%m/%d %H:%M:%S", time.localtime(time.time())
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
                + "\nOut of {} servers\n".format(numServ)
                + "Key:"
                + (
                    str(search)
                    .replace("'", '"')
                    .replace("ObjectId(", "")
                    .replace(")", "")
                    .replace("None", "null")
                    .replace("True", "true")
                    .replace("False", "false")
                    if search != {}
                    else "---n/a---"
                )
                + "/|\\"
                + str(index)
                + "\n",
            ),
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

                    self.logger.print("Favicon added")
                else:
                    _file = None
            else:
                _file = None
        except Exception:
            self.logger.error(traceback.format_exc())
            _file = None

        players = info
        if players is not None and "lastOnlinePlayersList" in players:
            players = players["lastOnlinePlayersList"]
        else:
            players = []

        buttons = [
            interactions.Button(
                label="Show Players",
                custom_id="show_players",
                style=interactions.ButtonStyle.PRIMARY,
                disabled=(len(players) == 0),
            ),
            interactions.Button(
                label="Next Server",
                custom_id="rand_select",
                style=interactions.ButtonStyle.PRIMARY,
                disabled=not (numServ > 1),
            ),
            interactions.Button(
                label="Join",
                custom_id="join",
                style=interactions.ButtonStyle.PRIMARY,
                disabled=not online or not allowJoin,
            ),
        ]

        row = interactions.ActionRow(
            components=buttons  # pyright: ignore [reportGeneralTypeIssues]
        )

        self.update(info)
        return embed, _file, row

    def join(
        self, ip: str, port: int, player_username: str, version: int = -1
    ) -> ServerType:
        try:
            # get info on the server
            server = mcstatus.JavaServer.lookup(ip + ":" + str(port))
            version = server.status().version.protocol if version == -1 else version

            connection = mcstatus.protocol.connection.TCPSocketConnection(
                (ip, port))

            # Send handshake packet: ID, protocol version, server address, server port, intention to login
            # This does not change between versions
            handshake = mcstatus.protocol.connection.Connection()

            handshake.write_varint(0)  # Packet ID
            handshake.write_varint(version)  # Protocol version
            handshake.write_utf(ip)  # Server address
            handshake.write_ushort(int(port))  # Server port
            handshake.write_varint(2)  # Intention to login

            connection.write_buffer(handshake)

            # Send login start packet: ID, username, include sig data, has uuid, uuid
            loginStart = mcstatus.protocol.connection.Connection()

            if version > 760:
                loginStart.write_varint(0)  # Packet ID
                loginStart.write_utf(player_username)  # Username
            else:
                loginStart.write_varint(0)  # Packet ID
                loginStart.write_utf(player_username)  # Username
            connection.write_buffer(loginStart)

            # Read response
            response = connection.read_buffer()
            id: int = response.read_varint()
            if id == 2:
                self.logger.debug("Logged in successfully")
                return ServerType(ip, version, "CRACKED")
            elif id == 0:
                self.logger.debug("Failed to login")
                self.logger.debug(response.read_utf())
                return ServerType(ip, version, "UNKNOW")
            elif id == 1:
                self.logger.debug("Encryption requested")
                return ServerType(ip, version, "PREMIUM")
            else:
                self.logger.debug("Unknown response: " + str(id))
                try:
                    reason = response.read_utf()
                except:
                    reason = "Unknown"

                self.logger.debug("Reason: " + reason)
                return ServerType(ip, version, "UNKNOW")
        except TimeoutError:
            self.logger.error("Server timed out")
            return ServerType(ip, version, "OFFLINE")
        except OSError:
            self.logger.error("Server did not respond")
            return ServerType(ip, version, "UNKNOW")
        except Exception:
            self.logger.error(traceback.format_exc())
            return ServerType(ip, version, "OFFLINE")

    def update(self, server: dict) -> None:
        """Spawns a thread to update a server

        Args:
            server (dict): The server to update
        """
        threading.Thread(target=self.check, args=(server["host"],)).start()
