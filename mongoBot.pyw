"""This is the discord bot for the mongoDB server list
"""
# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportOptionalMemberAccess=false

import asyncio
import json
import random
import sys
import time
import traceback

import interactions
import pymongo
import requests
from bson.errors import InvalidId
from bson.objectid import ObjectId
from interactions import slash_command

import utils
from utils import text

autoRestart = False
allowJoin = False
DEBUG = False
try:
    from privVars import *
except ImportError:
    MONGO_URL = "mongodb+srv://..."
    TOKEN = "..."

if MONGO_URL == "mongodb+srv://...":
    print("Please add your mongo url to privVars.py")
    input()
    sys.exit()
if TOKEN == "...":
    print("Please add your bot token to privVars.py")
    input()
    sys.exit()

# Setup
# ---------------------------------------------

client = pymongo.MongoClient(MONGO_URL, server_api=pymongo.server_api.ServerApi("1"))  # type: ignore
db = client["mc"]
col = db["servers"]

utils = utils.utils(col, debug=DEBUG, allowJoin=allowJoin)
logger = utils.logger
databaseLib = utils.database
finderLib = utils.finder
playerLib = utils.players
serverLib = utils.server
text = utils.text

bot = interactions.Client(
    token=TOKEN,
    intents=interactions.Intents.GUILD_MESSAGES
    | interactions.Intents.GUILDS
    | interactions.Intents.GUILD_INTEGRATIONS,
    status=interactions.Status.ONLINE,
    activity=interactions.Activity(
        type=interactions.ActivityType.WATCHING, name="for servers"
    ),
    logger=logger,
)

default_pipeline = [
    {
        "$match": {
            "$and": [
                {"lastOnlinePlayersMax": {"$gt": 0}},
                {"lastOnlinePlayers": {"$gt": 0}},
            ]
        }
    },
]


def print(*args, **kwargs):
    logger.print(" ".join(map(str, args)), **kwargs)


def timeNow():
    return text.timeNow()


# Commands
# ---------------------------------------------


@slash_command(
    name="find",
    description="Find a server",
    options=[
        interactions.SlashCommandOption(
            name="_id",
            type=interactions.OptionType.STRING,
            description="The ID of the server",
            required=False,
        ),
        # interactions.SlashCommandOption(
        #     name="host",
        #     description="The host of the server",
        #     type=interactions.OptionType.STRING,
        #     required=False,
        # ),
        # interactions.SlashCommandOption(
        #     name="port",
        #     description="The port of the server",
        #     type=interactions.OptionType.INTEGER,
        #     required=False,
        # ),
        interactions.SlashCommandOption(
            name="player",
            description="The player to search for (uuid or player name) **WIP**",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.SlashCommandOption(
            name="version",
            description="The version of the server",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.SlashCommandOption(
            name="motd",
            description="The motd of the server",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.SlashCommandOption(
            name="max_players",
            description="The max players of the server",
            type=interactions.OptionType.INTEGER,
            required=False,
            min_value=0,
        ),
        interactions.SlashCommandOption(
            name="cracked",
            description="If the server blocks the EULA",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
        interactions.SlashCommandOption(
            name="has_favicon",
            description="If the server has a favicon",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def find(
    ctx: interactions.InteractionContext,
    _id: str = None,
    host: str = None,
    port: int = None,
    player: str = None,
    version: str = None,
    motd: str = None,
    max_players: int = None,
    cracked: bool = None,
    has_favicon: bool = None,
):
    """Find a server

    Args:
        ctx (interactions.InteractionContext): The context of the command
        _id (str, optional): The ID of the server. Defaults to None.
        host (str, optional): The host of the server. Defaults to None.
        player (str, optional): The player to search for. Defaults to None.
        version (str, optional): The version of the server. Defaults to None.
        motd (str, optional): The motd of the server. Defaults to None.
        port (int, optional): The port of the server. Defaults to 25565.
        max_players (int, optional): The max players of the server. Defaults to -1.
        cracked (bool, optional): If the server blocks the EULA. Defaults to False.
        has_favicon (bool, optional): If the server has a favicon. Defaults to False.
    """

    print(
        "find",
        "id:" + str(_id),
        "host:" + str(host),
        "port:" + str(port),
        'player:"' + str(player) + '"',
        'version:"' + str(version) + '"',
        'motd:"' + str(motd) + '"',
        "max_players:" + str(max_players),
        "cracked:" + str(cracked),
        "has_favicon:" + str(has_favicon),
    )

    # send as embed
    await ctx.defer()

    # pipline that matches version name case-insensitive, motd case-insensitive, max players, cracked and has favicon
    pipeline = [{"$match": {"$and": []}}]

    pipeline[0]["$match"]["$and"].append({"lastOnlinePlayersMax": {"$gt": 0}})
    pipeline[0]["$match"]["$and"].append({"lastOnlinePlayers": {"$lte": 100000}})
    info = {}
    flag = False
    numServers = 0
    msg = await ctx.send(
        embed=interactions.Embed(
            title="Searching...",
            description="Please wait while we search for servers",
            color=finderLib.BLUE,
        ),
        components=finderLib.disButtons(),
    )
    # if parameters are given, add them to the search

    # special matching
    if host is not None:
        validServ = True
        # check if the given host is a valid server
        if host.replace(".", "").isdigit():
            serverList = [col.find_one({"host": host})]
            if serverList[0] is None:
                serverList = [col.find_one({"hostname": host})]
        else:
            serverList = [col.find_one({"hostname": host})]
            if serverList[0] is None:
                serverList = [col.find_one({"host": host})]

        if serverList[0] is None:
            logger.print("Server not in database")
            # try to get the server info from check
            info = finderLib.check(host, port)

            if info is None:
                logger.print("Server not online")
                validServ = False
            else:
                serverList = col.find_one({"host": info["host"]})

        if validServ:
            flag = True
            numServers = 1
            pipeline[0]["$match"]["$and"].append(
                {"_id": ObjectId(serverList[0]["_id"])}
            )
        else:
            # search the database for servers with similar hostnames
            # search with regex applied to 'hostname' and 'host' of .*host.*
            pipeline[0]["$match"]["$and"].append(
                {
                    "$or": [
                        {"hostname": {"$regex": ".*" + host + ".*"}},
                        {"host": {"$regex": ".*" + host + ".*"}},
                    ]
                }
            )
    if _id is not None:
        # check that _id is valid
        if len(_id) != 12 and len(_id) != 24:
            logger.print("Invalid ID: " + str(len(_id)))
            await msg.edit(
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description="Invalid ID",
                        timestamp=timeNow(),
                        color=finderLib.RED,
                    )
                ],
                components=finderLib.disButtons(),
            )
            return
        else:
            logger.print("Valid ID: " + _id)

        try:
            res = col.find({"_id": ObjectId(_id)})
        except InvalidId:
            logger.print("Invalid ID for ObjectID: " + _id)
            await msg.edit(
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description="Invalid ID",
                        timestamp=timeNow(),
                        color=finderLib.RED,
                    )
                ],
                components=finderLib.disButtons(),
            )
            return
        logger.print(res)
        flag = True

        if res is None:
            logger.print("Server not found")
            await msg.edit(
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description="Server not found",
                        timestamp=timeNow(),
                        color=finderLib.RED,
                    )
                ],
                components=finderLib.disButtons(),
            )
            return
        else:
            logger.print("Server found")
            numServers = 1
    if player is not None:
        flag = True
        name = ""
        uuid = ""
        isID = len(player) > 16

        if isID:
            url = (
                "https://sessionserver.mojang.com/session/minecraft/profile/"
                + player.replace("-", "")
            )
        else:
            url = "https://api.mojang.com/users/profiles/minecraft/" + player

        resp = requests.get(url)
        jresp = resp.json()

        if "error" in resp.text or resp.text == "":  # if the player is not found
            logger.print("Player not found in minecraft api")
            await msg.edit(
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description=f"{player} not found in minecraft api",
                        timestamp=timeNow(),
                        color=finderLib.RED,
                    )
                ],
                components=finderLib.disButtons(),
            )
            return
        else:
            uuid = jresp["id"]
            name = jresp["name"]

        pipeline[0]["$match"]["$and"].append(
            {"lastOnlinePlayersList.uuid": uuid.replace("-", "")}
        )

        logger.print(pipeline)

        serverList = col.aggregate(pipeline)
        numServers = col.count_documents(pipeline[0]["$match"])

        logger.print("Finding player", player)
        face = utils.players.playerHead(name)
        
        if face is None:
            await ctx.send(
                emebeds=[
                    interactions.Embed(
                        title="Error",
                        description=f"Could not find {name}'s skin",
                        color=finderLib.RED,
                        timestamp=timeNow(),
                    ),
                ],
                ephermeral=True,
            )

        if numServers == 0:
            logger.print("Player not found in database")
            embeds = [
                interactions.Embed(
                    title="Error",
                    description=f"{player} not found in database",
                    color=finderLib.RED,
                    timestamp=timeNow(),
                )
            ]
            embeds[0].set_thumbnail(url="attachment://playerhead.png") if face is not None else None

            await msg.edit(
                embeds=embeds,
                components=finderLib.disButtons(),
                file=face if face is not None else None,
            )
            return

        embed = interactions.Embed(
            title=f"{name} found",
            description=f"Found {name} in {numServers} servers",
            color=finderLib.GREEN,
            timestamp=timeNow(),
        )
        embed.set_thumbnail(url="attachment://playerhead.png") if face is not None else None

        await msg.edit(
            embeds=[embed],
            components=finderLib.disButtons(),
            file=face if face is not None else None,
        )

    if version is not None:
        pipeline[0]["$match"]["$and"].append(
            {"lastOnlineVersion": {"$regex": ".*" + version + ".*", "$options": "i"}}
        )
    if motd is not None:
        pipeline[0]["$match"]["$and"].append(
            {"lastOnlineDescription": {"$regex": ".*" + motd + ".*", "$options": "i"}}
        )
    if max_players is not None:
        pipeline[0]["$match"]["$and"].append({"lastOnlinePlayersMax": max_players})
    if cracked is not None:
        pipeline[0]["$match"]["$and"].append({"cracked": cracked})
    if has_favicon is not None:
        if has_favicon:
            pipeline[0]["$match"]["$and"].append(
                {
                    "$expr": {
                        "$and": [
                            {"$ne": ["$favicon", None]},
                            {"$gt": [{"$strLenCP": "$favicon"}, 10]},
                        ]
                    }
                }
            )
        else:
            pipeline[0]["$match"]["$and"].append(
                {
                    "$expr": {
                        "$or": [
                            {"$eq": ["$favicon", None]},
                            {"$lte": [{"$strLenCP": "$favicon"}, 10]},
                        ]
                    }
                }
            )

    if (
        pipeline
        == [
            {
                "$match": {
                    "$and": [
                        {"lastOnlinePlayersMax": {"$gt": 0}},
                        {"lastOnlinePlayers": {"$lte": 100000}},
                    ]
                }
            }
        ]
        and not flag
    ):
        await msg.edit(
            embeds=[
                interactions.Embed(
                    title="Error",
                    description="No search parameters given",
                    color=finderLib.YELLOW,
                    timestamp=timeNow(),
                )
            ],
            components=finderLib.disButtons(),
        )
    else:
        try:
            # get server info
            if not flag:
                serverList = []
                logger.print("Flag is down, getting server info from database")
                numServers = col.count_documents(pipeline[0]["$match"])
                logger.print(f"Number of servers: {numServers}")
                serverList = col.aggregate(pipeline)
            else:
                pipeline = (
                    {}
                    if pipeline
                    == [
                        {
                            "$match": {
                                "$and": [
                                    {"lastOnlinePlayersMax": {"$gt": 0}},
                                    {"lastOnlinePlayers": {"$lte": 100000}},
                                ]
                            }
                        }
                    ]
                    else pipeline
                )
                logger.print("Flag is up, setting server info")

            logger.print(f"Servers:{numServers}|Search:{pipeline}|Flag:{flag}")
            if numServers == 0:
                logger.print("No servers found in database")
                await msg.edit(
                    embeds=[
                        interactions.Embed(
                            title="Error",
                            description="No servers found",
                            color=finderLib.YELLOW,
                            timestamp=timeNow(),
                        )
                    ],
                )
                return

            await msg.edit(
                embeds=[
                    interactions.Embed(
                        title="Searching...",
                        description="Getting info about a server out of "
                        + str(numServers)
                        + " servers...",
                        timestamp=timeNow(),
                        color=finderLib.BLUE,
                    )
                ],
                components=finderLib.disButtons(),
            )

            # setup the embed
            embed = finderLib.genEmbed(
                index=0, numServ=numServers, search=pipeline, allowJoin=allowJoin
            )
            _file = embed[1]
            comps = embed[2]
            embed = embed[0]

            logger.print("Embed generated", embed, comps, _file)

            # send the embed sometimes with the favicon
            if _file:
                await msg.edit(embed=embed, file=_file, components=comps)
            else:
                await msg.edit(embed=embed, components=comps)
        except Exception:
            logger.print(traceback.format_exc())
            await msg.edit(
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description="An error occurred while searching. Please try again later and check the logs for "
                        "more details.",
                        color=finderLib.RED,
                        timestamp=timeNow(),
                    )
                ],
                components=finderLib.disButtons(),
            )
            print(
                f"----\n{traceback.format_exc()}\n====\n{type(info)}\n====\n{info}\n----"
            )


@interactions.component_callback("show_players")
async def show_players(ctx: interactions.ComponentContext):
    try:
        msg = ctx.message

        await ctx.defer(ephemeral=True)

        host = msg.embeds[0].title[2:]  # exclude the online symbol

        players = utils.players.playerList(host)

        random.shuffle(players)  # for servers with more than 25 logged players

        embed = interactions.Embed(
            title="Players",
            description="{} players logged".format(len(players)),
            timestamp=timeNow(),
            color=finderLib.GREEN,
        )

        for player in players:
            try:
                # check if online is in the dict
                if "online" not in player:
                    player["online"] = False
                embed.add_field(
                    name=("🟢 " if player["online"] else "🔴 ") + player["name"],
                    value="`{}`".format(player["uuid"]),
                    inline=True,
                )
            except Exception:
                print(traceback.format_exc())
                print(player)
                break

        logger.print(embed, "\n---\n", players)

        await ctx.send(embeds=[embed], ephemeral=True)
    except Exception:
        print(traceback.format_exc(), ctx.message)
        await ctx.send(
            embeds=[
                interactions.Embed(
                    title="Error",
                    description="An error occured while searching. Please try again later and check the logs for more details.",
                    color=finderLib.RED,
                    timestamp=timeNow(),
                )
            ],
            ephemeral=True,
        )


@interactions.component_callback("rand_select")
async def next(ctx: interactions.ComponentContext):
    await rand_select(ctx)


async def rand_select(
    ctx: interactions.ComponentContext,
    _index: int = None,
    orginal: interactions.Message = None,
):
    org = orginal if orginal is not None else ctx.message
    try:
        logger.print("Fetching message")
        oldMsg = ctx.message.embeds[0]
        logger.print(str(oldMsg.title))

        if "---n/a---" in oldMsg.footer.text:
            return

        await ctx.defer(edit_origin=True) if orginal is None else None

        msg = await org.edit(
            embeds=[
                interactions.Embed(
                    title="Loading...",
                    description="Loading the next server...",
                    color=finderLib.BLUE,
                    timestamp=timeNow(),
                    footer=interactions.EmbedFooter(
                        text="Key:---n/a---/|\\0"
                    ),  # key and index
                )
            ],
            components=finderLib.disButtons(),
        )

        text = oldMsg.footer.text
        text = text.split("\n")[2]
        text = text.split("Key:")[1]
        text = text.split("/|\\")

        key = text[0]
        index = int(text[1])
        logger.print("Index: " + str(index))
        logger.print("Key: " + key)

        key = json.loads(key) if key != "---n/a---" else {}
        if key == {}:  # if the key is empty, return
            return

        logger.print("ReGenerating list")
        numServers = col.count_documents(key[0]["$match"])
        logger.print("List generated: " + str(numServers) + " servers")
        index = ((index + 1) if (index + 1 < numServers) else 0) if _index is None else _index

        info = finderLib.get_doc_at_index(col, key, index)
        if info is None:
            logger.print(
                "Error: No server found at index "
                + str(index)
                + " out of "
                + str(numServers)
                + " servers"
            )
            return

        msg = await msg.edit(
            embeds=[
                interactions.Embed(
                    title="Loading...",
                    description="Loading {}...".format(info["host"]),
                    color=finderLib.BLUE,
                    timestamp=timeNow(),
                    footer=interactions.EmbedFooter(
                        text="Key:---n/a---/|\\{}".format(index)
                    ),
                ),
            ],
            components=finderLib.disButtons(),
        )

        embed = finderLib.genEmbed(
            search=key, index=index, numServ=numServers, allowJoin=allowJoin
        )
        _file = embed[1]
        button = embed[2]
        embed = embed[0]

        logger.print("Embed generated", embed, button, _file)

        if _file:
            msg = await msg.edit(embeds=[embed], files=[_file], components=button)
        else:
            msg = await msg.edit(embeds=[embed], components=button)
    except Exception:
        logger.error(traceback.format_exc())
        await ctx.send(
            embeds=[
                interactions.Embed(
                    title="Error",
                    description="An error occured while searching. Please try again later and check the logs for more "
                    "details.",
                    color=finderLib.RED,
                    timestamp=timeNow(),
                )
            ],
            components=finderLib.disButtons(),
        )


async def emailModal(ctx: interactions.ComponentContext, host: str):
    textInp = interactions.ShortText(
        label="Email",
        custom_id="email",
        placeholder="pilot1782@verygooddomain.com",
        min_length=1,
        max_length=100,
    )
    modal = interactions.Modal(
        textInp,
        title="Email for " + host,
        custom_id="email_modal",
    )

    await ctx.send_modal(modal)

    try:
        modal_ctx = await ctx.bot.wait_for_modal(modal, timeout=60)

        email = modal_ctx.responses["email"]

        await emailModalResponse(modal_ctx, email)
    except asyncio.TimeoutError:
        pass


@interactions.component_callback("join")
async def joinServer(ctx: interactions.ComponentContext):
    """Join a server"""
    # get the original message
    msg = ctx.message.embeds[0]
    host = msg.title[2:]  # exclude the online symbol

    # clear nmp cache
    serverLib.clearNMPCache()

    # spawn a text box to ask for an email
    await emailModal(ctx, host)


async def emailModalResponse(ctx: interactions.ModalContext, email: str):
    modal = ctx.message.embeds[0].title
    host = modal[2:]

    await ctx.defer(ephemeral=True)

    serverLib.start(
        ip=host,
        port=25565,
        username=email,
    )

    while serverLib.getState() == "NOT_CONNECTED":
        await asyncio.sleep(0.1)

    if "AUTHENTICATING:" in serverLib.getState():
        code = serverLib.getState().split("AUTHENTICATING:")[1]
        logger.print("Code: " + code)

        await ctx.send(
            embeds=[
                interactions.Embed(
                    title="Authentication required",
                    description="Please enter the code `{}` at https://www.microsoft.com/link in order to "
                    "authenticate.\nYou will have three minutes before the code expires.".format(
                        code
                    ),
                    color=finderLib.BLUE,
                )
            ],
            ephemeral=True,
        )

        tStart = time.time()
        while "AUTHENTICATING:" in serverLib.getState() and time.time() - tStart < 180:
            await asyncio.sleep(1)

        if "AUTHENTICATING:" in serverLib.getState():
            await ctx.send(
                embeds=[
                    interactions.Embed(
                        title="Authentication required",
                        description="The code has expired. Please try again.",
                        color=finderLib.RED,
                    )
                ],
                ephemeral=True,
            )
            return
        else:
            await ctx.send(
                embeds=[
                    interactions.Embed(
                        title="Join server",
                        description="Connecting to {}...".format(host),
                        color=finderLib.ORANGE,
                    )
                ],
                ephemeral=True,
            ) if DEBUG else None

    logger.print("state: " + serverLib.getState())
    while serverLib.getState() == "CONNECTING":
        await asyncio.sleep(0.1)

    if serverLib.getState() == "CONNECTED":
        print("Connected")

        serverInfo = serverLib.getInfo()
        players = serverInfo["names"]
        position = serverInfo["position"]
        heldItem = serverInfo["heldItem"]
        inv = serverInfo["inventory"]

        # update player list
        dbVal = col.find_one({"host": host})
        players2 = []
        for player in players:
            url = "https://api.mojang.com/users/profiles/minecraft/{}".format(player)
            uuid = (
                requests.get(url).json()["id"]
                if "id" in requests.get(url).json()
                else ""
            )
            if uuid == "":
                continue

            player = {
                "name": player,
                "uuid": uuid,
            }
            players2.append(player)
            if player not in dbVal["lastOnlinePlayersList"]:
                dbVal["lastOnlinePlayersList"].append(player)
        players = players2

        plyOnline = len(players)
        col.update_one(
            {"host": host},
            {"$set": {"players": dbVal["lastOnlinePlayersList"]}},
            upsert=True,
        )

        players2 = []
        for player in dbVal["lastOnlinePlayersList"]:
            player["online"] = player in players
            players2.append(player)
        players = players2

        embed = interactions.Embed(
            title="Join Server",
            description="Done! You spawned at {} with {} players holding a(n) {}.".format(
                position, plyOnline, heldItem
            ),
            color=finderLib.GREEN,
            timestamp=timeNow(),
        ).set_footer("Powered by MineFlayer")

        for player in players:
            embed.add_field(
                name=(
                    player["name"] + (" (Online)" if player["online"] else " (Offline)")
                ),
                value="`" + player["uuid"] + "`",
                inline=True,
            )

        logger.print("Inventory: " + str(inv))
        items = str(i.display_name for i in inv)

        embed.add_field(
            name="Inventory",
            value=items,
            inline=False,
        )

        await ctx.send(embeds=[embed], ephemeral=True)
        serverLib.clearNMPCache()
        return

    if serverLib.getState().startswith("DISCONNECTED"):
        reason = serverLib.getState().split("DISCONNECTED:")[1]
        if reason == "WHITELISTED":
            # update the server to be whitelisted
            col.update_one(
                {"host": host},
                {"$set": {"whitelisted": True}},
                upsert=True,
            )

            await ctx.send(
                embeds=[
                    interactions.Embed(
                        title="Join Server",
                        description="Error: This server is whitelisted or you are banned. Please contact the server "
                        "owner to be allowed back in.",
                        color=finderLib.YELLOW,
                        timestamp=timeNow(),
                    )
                ],
                ephemeral=True,
            )
        else:
            print("Error")

        serverLib.clearNMPCache()
        return

    await ctx.send(  # failed to join
        embeds=[
            interactions.Embed(
                title="Join Server",
                description="Error: {}".format(serverLib.getState()),
                color=finderLib.RED,
                timestamp=timeNow(),
            )
        ],
        ephemeral=True,
    )
    serverLib.clearNMPCache()


@interactions.component_callback("jump")
async def jump(ctx: interactions.ComponentContext):
    """Jump to a certain index"""
    org = ctx.message

    total = int(org.embeds[0].footer.text.split("Out of ")[-1].split(" ")[0])

    textInp = interactions.ShortText(
        label="Jump to index",
        placeholder="Enter a number between 1 and {}".format(total),
        min_length=1,
        max_length=len(str(total)),
        custom_id="jump",
    )

    modal = interactions.Modal(
        textInp,
        title="Jump to index",
        custom_id="jump_modal",
    )
    await ctx.send_modal(modal)

    try:
        modal_ctx = await ctx.bot.wait_for_modal(modal=modal, timeout=60)

        index = int(modal_ctx.responses["jump"])

        if index < 1 or index > total:
            await modal_ctx.send(
                embeds=[
                    interactions.Embed(
                        title="Jump to index",
                        description="Error: Invalid index",
                        color=finderLib.RED,
                    )
                ],
                ephemeral=True,
            )
            return

        await modal_ctx.send(
            embed=interactions.Embed(
                title="Jump to index",
                description="Jumping to index {}...".format(index - 1),
                color=finderLib.ORANGE,
            ),
            ephemeral=True,
        )

        await rand_select(ctx, _index=index - 1, orginal=org)
    except asyncio.TimeoutError:
        return


@slash_command(
    name="stats",
    description="Get stats about the database",
)
async def stats(ctx: interactions.SlashContext):
    await ctx.defer()
    try:
        """Get stats about the database"""

        msg = await ctx.send(
            embeds=[
                interactions.Embed(
                    title="Stats",
                    description="Getting stats...",
                    timestamp=timeNow(),
                    color=finderLib.BLUE,
                )
            ]
        )

        logger.print("Getting stats...")

        serverCount = col.count_documents({})
        # add commas to server count
        serverCount = "{:,}".format(serverCount)
        text = f"Total servers: `{serverCount}`\nPlayer Count: `...`\nPlayers logged: `...`\nMost common version:\n`...`"
        msg = await ctx.edit(
            message=msg,
            embeds=[
                interactions.Embed(
                    title="Stats",
                    description=text,
                    timestamp=timeNow(),
                    color=finderLib.BLUE,
                )
            ],
        )

        logger.print("Getting versions...")
        versions = await databaseLib.get_sorted_versions(col)
        topTen = [x["version"] for x in versions[:10]]

        text = "Total servers: `{}`\nRough Player Count: `...`\nMost common version:```css\n{}\n```".format(
            serverCount, ("\n".join(topTen[:5]))
        )
        msg = await ctx.edit(
            message=msg,
            embeds=[
                interactions.Embed(
                    title="Stats",
                    description=text,
                    timestamp=timeNow(),
                    color=finderLib.BLUE,
                )
            ],
        )

        logger.print("Getting player count...")
        players = await databaseLib.get_total_players_online(col)
        # add commas to player count
        players = "{:,}".format(players)

        logger.print("Getting players logged...")
        pLogged = await databaseLib.getPlayersLogged(col)
        pLogged = "{:,}".format(pLogged)
        text = "Total servers: `{}`\nRough Player Count: `{}`\nPlayers logged: `{}`\nMost common version:```css\n{}\n```".format(
            serverCount, players, pLogged, ("\n".join(topTen[:5]))
        )

        print(
            f"Total servers: {serverCount}\nRough Player Count: {pLogged}/{players}\nMost common versions: {topTen}"
        )

        msg = await ctx.edit(
            message=msg,
            embeds=[
                interactions.Embed(
                    title="Stats",
                    description=text,
                    timestamp=timeNow(),
                    color=finderLib.BLUE,
                )
            ],
        )
    except Exception:
        print(f"====\nError: {traceback.format_exc()}\n====")
        logger.print(traceback.format_exc())

        await ctx.send(
            embeds=[
                interactions.Embed(
                    title="Error",
                    description="Error getting stats, check the console and log for more info.",
                    timestamp=timeNow(),  # local time
                )
            ],
            ephemeral=True,
        )


@slash_command(
    name="help",
    description="Get help",
)
async def help_list(ctx: interactions.InteractionContext):
    """Get help"""
    await ctx.send(
        embeds=[
            interactions.Embed(
                title="Help",
                description="""Commands:
`/find` - Find a server
```markdown
*Arguments:*
`host` - The host of the server to ping (not a search argument, and if included will ignore all other arguments except `port`)
....`port` - The port of the server (optional and only used when `host` is included, note that `host:port` is supported instead of using this argument)
....If the passed host is not a valid server ie: hypixel.net, it will be treated as a search argument and find servers with similar hostnames, hypixel.net would return mc.hypixel.net

`player` - The name or uuid of a player

`_id` - The id of the server in the database

`version` - The version of the server
`players` - The max amount of players on the server
`motd` - The description of the server
`cracked` - If the server is cracked or not

*Returns:*
A list of servers that match the search
`hostname` - The hostname of the server (optional)
`motd` - The description of the server
`version` - The version of the server
`players` - The amount of players on the server
`maxPlayers` - The max amount of players on the server
`cracked` - If the server is cracked or not
`whitelisted` - If the server is whitelisted or not
`ping` - The ping of the server
`lastOnline` - The last time the server was online
```

`/stats` - Get stats about the database

`/help` - This message
""",
                timestamp=timeNow(),  # local time
                color=finderLib.BLUE,
            )
        ],
        ephemeral=True,
    )


# on ready
@interactions.listen()
async def on_ready():
    user = await bot.fetch_user(bot.user.id)
    logger.print("Bot is signed in as {}".format(user.username))


# Run the bot
# ---------------------------------------------


if __name__ == "__main__":
    try:
        bot.start()
    except Exception as e:
        if e == KeyboardInterrupt:
            asyncio.run(bot.stop())
            sys.exit()
        else:
            logger.error(traceback.format_exc())
