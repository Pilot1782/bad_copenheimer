"""This is the discord bot for the mongoDB server list
"""
# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportOptionalMemberAccess=false

import datetime
import json
import random
import sys
import time
import traceback

import interactions
from mcstatus import server
import pymongo
import requests
from bson.errors import InvalidId
from bson.objectid import ObjectId
from interactions.api.models import Message
from interactions.ext.files import (command_edit, command_send, component_edit,
                                    component_send)

from funcs import funcs

autoRestart = False
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

bot = interactions.Client(
    token=TOKEN, intents=interactions.Intents.GUILD_MESSAGE_CONTENT
)

client = pymongo.MongoClient(MONGO_URL, server_api=pymongo.server_api.ServerApi("1"))  # type: ignore
db = client["mc"]
col = db["servers"]

fncs = funcs(collection=col)


def print(*args, **kwargs):
    fncs.print(" ".join(map(str, args)), **kwargs)


def timeNow():
    # return local time
    return datetime.datetime.now(
        datetime.timezone(
            datetime.timedelta(hours=0)  # no clue why this is needed but it works now?
        )
    ).strftime("%Y-%m-%d %H:%M:%S")


# Commands
# ---------------------------------------------


@bot.command(
    name="find",
    description="Find a server",
    options=[
        interactions.Option(
            name="_id",
            type=interactions.OptionType.STRING,
            description="The ID of the server",
            required=False,
        ),
        interactions.Option(
            name="host",
            description="The host of the server",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="port",
            description="The port of the server",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="player",
            description="The player to search for (uuid or player name) **WIP**",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="version",
            description="The version of the server",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="motd",
            description="The motd of the server",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="maxplayers",
            description="The max players of the server",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        interactions.Option(
            name="cracked",
            description="If the server blocks the EULA",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
        interactions.Option(
            name="hasfavicon",
            description="If the server has a favicon",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def find(
    ctx: interactions.CommandContext,
    _id: str = "",
    player: str = "",
    version: str = "",
    host: str = "",
    port: int = 25565,
    motd: str = "",
    maxplayers: int = -1,
    cracked: bool = False,
    hasfavicon: bool = False,
):
    """Find a server

    Args:
        _id (str, optional): The ID of the server. Defaults to None.
        host (str, optional): The host of the server. Defaults to None.
        Player (str, optional): The player to search for. Defaults to None.
        version (str, optional): The version of the server. Defaults to None.
        motd (str, optional): The motd of the server. Defaults to None.
        port (int, optional): The port of the server. Defaults to 25565.
        maxplayers (int, optional): The max players of the server. Defaults to -1.
        cracked (bool, optional): If the server blocks the EULA. Defaults to False.
        hasfavicon (bool, optional): If the server has a favicon. Defaults to False.
    """

    print(
        "find",
        "id:" + _id,
        "host:" + host,
        "port:" + str(port),
        'player:"' + player + '"',
        'version:"' + version + '"',
        'motd:"' + motd + '"',
        "maxplayers:" + str(maxplayers),
        "cracked:" + str(cracked),
        "hasfavicon:" + str(hasfavicon),
    )

    # send as embed
    await ctx.defer()

    serverList = []
    # pipline that matches version name case insensitive, motd case insensitive, max players, cracked and has favicon
    pipeline = [{"$match": {"$and": []}}]
    
    pipeline[0]["$match"]["$and"].append({"lastOnlinePlayersMax": {"$gt": 0}})
    pipeline[0]["$match"]["$and"].append({"lastOnlinePlayers": {"$lte": 100000}})
    info = {}
    flag = False
    numServers = 0
    # if parameters are given, add them to the search

    # special matching
    if host:
        serverList = [None]
        if host.replace(".", "").isdigit():
            serverList = [col.find_one({"host": host})]
            if serverList[0] is None:
                serverList = [col.find_one({"hostname": host})]
        else:
            serverList = [col.find_one({"hostname": host})]
            if serverList[0] is None:
                serverList = [col.find_one({"host": host})]

        if serverList[0] is None:
            fncs.dprint("Server not in database")
            # try to get the server info from check
            info = fncs.check(host, port)

            if info is None:
                fncs.dprint("Server not online")
                await command_send(
                    ctx,
                    embeds=[
                        interactions.Embed(
                            title="Error",
                            description="Server not in database and not online",
                            timestamp=timeNow(),
                        )
                    ],
                    ephemeral=True,
                )
                return
            else:
                serverList = [info]

        flag = True
        numServers = 1
    if _id:
        # check that _id is vaild
        if len(_id) != 12 and len(_id) != 24:
            fncs.dprint("Invalid ID: " + str(len(_id)))
            await command_send(
                ctx,
                embeds=[
                    interactions.Embed(
                        title="Error", description="Invalid ID", timestamp=timeNow()
                    )
                ],
                ephemeral=True,
            )
            return
        else:
            fncs.dprint("Valid ID: " + _id)

        try:
            res = col.find({"_id": ObjectId(_id)})
        except InvalidId:
            fncs.dprint("Invalid ID for ObjectID: " + _id)
            await command_send(
                ctx,
                embeds=[
                    interactions.Embed(
                        title="Error", description="Invalid ID", timestamp=timeNow()
                    )
                ],
                ephemeral=True,
            )
            return
        fncs.dprint(res)
        flag = True

        if res is None:
            fncs.dprint("Server not found")
            await command_send(
                ctx,
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description="Server not found",
                        timestamp=timeNow(),
                    )
                ],
                ephemeral=True,
            )
            return
        else:
            fncs.dprint("Server found")
            serverList = res
            numServers = 1
    if player:
        search = {}
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
            fncs.dprint("Player not found in minecraft api")
            await command_send(
                ctx,
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description=f"{player} not found in minecraft api",
                        timestamp=timeNow(),
                    )
                ],
                ephemeral=True,
            )
            return
        else:
            uuid = jresp["id"]
            name = jresp["name"]

        pipeline[0]["$match"]["$and"].append(
            {"lastOnlinePlayersList.uuid": uuid.replace("-", "")}
        )

        fncs.dprint(pipeline)

        serverList = col.aggregate(pipeline)
        numServers = col.count_documents(pipeline[0]["$match"])

        fncs.dprint("Finding player", player)
        face = fncs.playerHead(name)

        if numServers == 0:
            fncs.dprint("Player not found in database")
            embeds = [
                interactions.Embed(
                    title="Error",
                    description=f"{player} not found in database",
                    color=0xFF6347,
                    timestamp=timeNow(),
                )
            ]
            embeds[0].set_thumbnail(url="attachment://playerhead.png")

            await command_send(ctx, embeds=embeds, files=[face], ephemeral=True)
            return

        embed = interactions.Embed(
            title=f"{name} found",
            description=f"Found {name} in {numServers} servers",
            color=0x00FF00,
            timestamp=timeNow(),
        )
        embed.set_thumbnail(url="attachment://playerhead.png")

        await command_send(ctx, embeds=[embed], files=[face])
    
    if version:
        pipeline[0]["$match"]["$and"].append({"lastOnlineVersion": {"$regex": ".*"+version+".*", "$options": "i"}})
    if motd:
        pipeline[0]["$match"]["$and"].append({"lastOnlineDescription": {"$regex": ".*"+motd+".*", "$options": "i"}})
    if maxplayers > 0:
        pipeline[0]["$match"]["$and"].append({"lastOnlinePlayersMax": maxplayers})
    if cracked:
        pipeline[0]["$match"]["$and"].append({"cracked": cracked})
    if hasfavicon:
        pipeline[0]["$match"]["$and"].append({
            "$expr": {
                "$and": [
                    {"$ne": ["$favicon", None]},
                    {"$gt": [{"$strLenCP": "$favicon"}, 10]}
                ]
            }
        })

    if pipeline == [{"$match": {"$and": [{"lastOnlinePlayersMax": {"$gt": 0}},{"lastOnlinePlayers": {"$lte": 100000}}]}}] and not flag:
        await command_send(
            ctx,
            embeds=[
                interactions.Embed(
                    title="Error",
                    description="No search parameters given",
                    color=0xFF6347,
                    timestamp=timeNow(),
                )
            ],
            ephemeral=True,
        )
    else:
        try:
            # get server info
            if not flag:
                serverList = []
                fncs.dprint("Flag is down, getting server info from database")
                numServers = col.count_documents(pipeline[0]["$match"])
                fncs.dprint(f"Number of servers: {numServers}")
                serverList = col.aggregate(pipeline)
            else:
                pipeline = {} if pipeline == [{"$match": {"$and": [{"lastOnlinePlayersMax": {"$gt": 0}},{"lastOnlinePlayers": {"$lte": 100000}}]}}] else pipeline
                fncs.dprint("Flag is up, setting server info")

            fncs.dprint(f"Servers:{numServers}|Search:{pipeline}|Flag:{flag}")
            await command_send(
                ctx,
                embeds=[
                    interactions.Embed(
                        title="Searching...",
                        description="Getting info about a server out of "
                        + str(numServers)
                        + " servers...",
                        timestamp=timeNow(),
                    )
                ],
            )
            
            # check that serverList is not empty
            if numServers == 0:
                fncs.dprint("No servers found in database")
                await command_send(
                    ctx,
                    embeds=[
                        interactions.Embed(
                            title="Error",
                            description="No servers found",
                            color=0xFF6347,
                            timestamp=timeNow(),
                        )
                    ],
                    ephemeral=True,
                )
                return
                

            # setup the embed
            embed = fncs.genEmbed(_serverList=serverList, index=0, numServ=numServers, search=pipeline)
            _file = embed[1]
            comps = embed[2]
            embed = embed[0]

            fncs.dprint("Embed generated", embed, comps, _file)

            # send the embed sometimes with the favicon
            if _file:
                await command_edit(ctx, embeds=[embed], files=[_file], components=comps)
            else:
                await command_edit(ctx, embeds=[embed], components=comps)
        except Exception:
            fncs.dprint(traceback.format_exc())
            await command_send(
                ctx,
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description="An error occured while searching. Please try again later and check the logs for more details.",
                        color=0xFF0000,
                        timestamp=timeNow(),
                    )
                ],
                ephemeral=True,
            )
            print(
                f"----\n{traceback.format_exc()}\n====\n{type(info)}\n====\n{info}\n----"
            )


@bot.component("show_players")
async def show_players(ctx: interactions.ComponentContext):
    try:
        msg = ctx.message

        await ctx.defer(ephemeral=True)

        host = msg.embeds[0].title[2:]  # exclude the online symbol

        players = fncs.playerList(host)

        random.shuffle(players)  # for servers with more than 25 logged players

        embed = interactions.Embed(
            title="Players",
            description="{} players logged".format(len(players)),
            timestamp=timeNow(),
        )

        for player in players:
            try:
                embed.add_field(
                    name=("🟢 " if player["online"] else "🔴 ") + player["name"],
                    value="`{}`".format(player["uuid"]),
                    inline=True,
                )
            except Exception:
                print(traceback.format_exc())
                print(player)
                break

        fncs.dprint(embed, "\n---\n", players)

        await component_send(ctx, embeds=[embed], ephemeral=True)
    except Exception:
        print(traceback.format_exc(), ctx.message)
        await component_send(
            ctx,
            embeds=[
                interactions.Embed(
                    title="Error",
                    description="An error occured while searching. Please try again later and check the logs for more details.",
                    color=0xFF0000,
                    timestamp=timeNow(),
                )
            ],
            ephemeral=True,
        )


@bot.component("rand_select")
async def rand_select(ctx: interactions.ComponentContext):
    try:
        fncs.dprint("Fetching message")
        msg = ctx.message.embeds[0]
        fncs.dprint(str(msg))

        if "---n/a---" in msg.footer.text:
            return

        await ctx.defer(edit_origin=True)

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

        await component_edit(
            ctx,
            embeds=[
                interactions.Embed(
                    title="Loading...",
                    description="Loading the next server...",
                    color=0x00FF00,
                    timestamp=timeNow(),
                    footer=interactions.EmbedFooter(
                        text="Key:---n/a---/|\\0"
                    ),  # key and index
                )
            ],
            components=[row],
        )

        text = msg.footer.text
        text = text.split("\n")[2]
        text = text.split("Key:")[1]
        text = text.split("/|\\")

        key = text[0]
        fncs.dprint("Key: " + key)
        index = int(text[1])
        fncs.dprint("Index: " + str(index))

        key = json.loads(key) if key != "---n/a---" else {}
        if key == {}:  # if the key is empty, return
            return
            

        fncs.dprint("ReGenerating list")
        serverList = col.aggregate(key)
        numServers = col.count_documents(key[0]["$match"])
        fncs.dprint("List generated: " + str(numServers) + " servers")
        index = (index + 1) if (index + 1 < numServers) else 0
        
        info = fncs.get_doc_at_index(col, key, index)
        if info == None:
            fncs.dprint("Error: No server found at index " + str(index) + " out of " + str(numServers) + " servers")
            return

        await component_edit(
            ctx,
            embeds=[
                interactions.Embed(
                    title="Loading...",
                    description="Loading {}...".format(info["host"]),
                    color=0x00FF00,
                    timestamp=timeNow(),
                    footer=interactions.EmbedFooter(
                        text="Key:---n/a---/|\\{}".format(index)
                    ),
                ),
            ],
            components=[row],
        )

        embed = fncs.genEmbed(_serverList=serverList, search=key, index=index, numServ=numServers)
        _file = embed[1]
        button = embed[2]
        embed = embed[0]

        fncs.dprint("Embed generated", embed, button, _file)

        if _file:
            await component_edit(ctx, embeds=[embed], files=[_file], components=button)
        else:
            await component_edit(ctx, embeds=[embed], components=button)
    except Exception:
        await component_send(
            ctx,
            embeds=[
                interactions.Embed(
                    title="Error",
                    description="An error occured while searching. Please try again later and check the logs for more details.",
                    color=0xFF0000,
                    timestamp=timeNow(),
                )
            ],
            ephemeral=True,
        )


@bot.command(
    name="stats",
    description="Get stats about the database",
)
async def stats(ctx: interactions.CommandContext):
    await ctx.defer()
    try:
        """Get stats about the database"""

        await ctx.send(
            embeds=[
                interactions.Embed(
                    title="Stats", description="Getting stats...", timestamp=timeNow()
                )
            ]
        )

        fncs.dprint("Getting stats...")

        serverCount = col.count_documents({})
        # add commas to server count
        serverCount = "{:,}".format(serverCount)
        text = f"Total servers: `{serverCount}`\nPlayer Count: `...`\nPlayers logged: `...`\nMost common version:\n`...`"
        await ctx.edit(
            embeds=[
                interactions.Embed(title="Stats", description=text, timestamp=timeNow())
            ]
        )

        fncs.dprint("Getting versions...")
        versions = await fncs.get_sorted_versions(col)
        topTen = [x["version"] for x in versions[:10]]

        text = "Total servers: `{}`\nRough Player Count: `...`\nMost common version:```css\n{}\n```".format(
            serverCount, ("\n".join(topTen[:5]))
        )
        await ctx.edit(
            embeds=[
                interactions.Embed(title="Stats", description=text, timestamp=timeNow())
            ]
        )

        fncs.dprint("Getting player count...")
        players = await fncs.get_total_players_online(col)
        # add commas to player count
        players = "{:,}".format(players)

        fncs.dprint("Getting players logged...")
        pLogged = await fncs.getPlayersLogged(col)
        pLogged = "{:,}".format(pLogged)
        text = "Total servers: `{}`\nRough Player Count: `{}`\nPlayers logged: `{}`\nMost common version:```css\n{}\n```".format(
            serverCount, players, pLogged, ("\n".join(topTen[:5]))
        )

        print(
            f"Total servers: {serverCount}\nRough Player Count: {pLogged}/{players}\nMost common versions: {topTen}"
        )

        await ctx.edit(
            embeds=[
                interactions.Embed(title="Stats", description=text, timestamp=timeNow())
            ]
        )
    except Exception:
        print(f"====\nError: {traceback.format_exc()}\n====")
        fncs.dprint(traceback.format_exc())

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


@bot.command(name="help")
async def help(ctx: interactions.CommandContext):
    """Get help"""
    await ctx.send(
        embeds=[
            interactions.Embed(
                title="Help",
                description="""Commands:
`/find` - Find a server
    *Arguments:*
        `host` - The host of the server
            `port` - The port of the server

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

`/stats` - Get stats about the database

`/help` - This message
""",
                timestamp=timeNow(),  # local time
            )
        ],
        ephemeral=True,
    )


# Run the bot
# ---------------------------------------------


if __name__ == "__main__":
    while True:
        try:
            bot.start()
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            else:
                print(e)
                fncs.dprint(traceback.format_exc())
                time.sleep(30)
                if autoRestart:
                    print("Restarting...")
                    continue
                else:
                    break
