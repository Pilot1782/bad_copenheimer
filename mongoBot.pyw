# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportOptionalMemberAccess=false
import datetime
import random
import requests
import sys
import time
import traceback
import json

import pymongo
from bson.objectid import ObjectId
from bson.errors import InvalidId
import interactions
from interactions.ext.files import (
    command_edit,
    component_edit,
    command_send,
    component_send,
)
from interactions.api.models import Message

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

bot = interactions.Client(token=TOKEN, intents=interactions.Intents.GUILD_MESSAGE_CONTENT)

client = pymongo.MongoClient(MONGO_URL, server_api=pymongo.server_api.ServerApi("1"))  # type: ignore
db = client["mc"]
col = db["servers"]

fncs = funcs(collection=col)


def print(*args, **kwargs):
    fncs.print(" ".join(map(str, args)), **kwargs)
    
def timeNow():
    # return local time
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=0))  # no clue why this is needed but it works now?
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
):
    """Find a server

    Args:
        _id (str, optional): The ID of the server. Defaults to None.
        host (str, optional): The host of the server. Defaults to None.
        Player (str, optional): The player to search for. Defaults to None.
        version (str, optional): The version of the server. Defaults to None.
        motd (str, optional): The motd of the server. Defaults to None.
        port (int, optional): The port of the server. Defaults to 25565.
    """

    print(
        "find",
        "id:"+_id,
        "host:"+host,
        "port:"+str(port),
        "player:\""+player+"\"",
        "version:\""+version+"\"",
        "motd:\""+motd+"\"",
        "maxplayers:"+str(maxplayers),
        "cracked:"+str(cracked)
    )

    # send as embed
    await ctx.defer()

    serverList = []
    search = {}
    info = {}
    _port = str(port)
    flag = False
    # if parameters are given, add them to the search
    
    if host:
        serverList = [col.find_one({"host": host})]

        if not serverList[0]:
            # try to get the server info from check
            info = fncs.check(host, port)

            if not info:
                serverList = []

        flag = True
        search = {}
    if version:
        search["lastOnlineVersion"] = version.lower()
    if motd:
        search["lastOnlineDescription"] = motd.lower()
    if maxplayers != -1:
        search["lastOnlinePlayersMax"] = maxplayers
    if cracked:
        search["cracked"] = cracked
    if _id:
        search = {}
        
        # check that _id is vaild
        if len(_id) != 12 and len(_id) != 24:
            fncs.dprint("Invalid ID: "+str(len(_id)))
            await command_send(
                ctx,
                embeds=[interactions.Embed(title="Error", description="Invalid ID", timestamp=timeNow())],
                ephemeral=True,
            )
            return
        else:
            fncs.dprint("Valid ID: "+_id)
        
        try:
            res = col.find_one({"_id": ObjectId(_id)})
        except InvalidId:
            fncs.dprint("Invalid ID for ObjectID: "+_id)
            await command_send(
                ctx,
                embeds=[interactions.Embed(title="Error", description="Invalid ID", timestamp=timeNow())],
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
            serverList = [res]
    if player:
        search = {}
        flag = True
        name = ""
        uuid = ""
        isID = len(player) > 16
        
        if isID:
            url = "https://sessionserver.mojang.com/session/minecraft/profile/"+player.replace("-", "")
        else:
            url = "https://api.mojang.com/users/profiles/minecraft/"+player

        resp = requests.get(url)
        jresp = resp.json()
        
        if "error" in resp.text or resp.text == "":  # if the player is not found
            fncs.dprint("UUID not found in minecraft api")
            await command_send(
                ctx,
                embeds=[
                    interactions.Embed(
                        title="Error",
                        description="UUID not found in minecraft api",
                        timestamp=timeNow(),
                    )
                ],
                ephemeral=True,
            )
            return
        else:
            uuid = jresp["id"]
            name = jresp["name"]

        serverList = list(col.find({"lastOnlinePlayersList": {"$elemMatch": {"uuid": uuid}}}))

        fncs.dprint("Finding player", player)
        face = fncs.playerHead(name)

        if serverList is None or len(serverList) == 0:
            fncs.dprint("Player not found in database")
            embeds = [
                    interactions.Embed(
                        title="Error",
                        description="Player not found in database",
                        color=0xFF6347,
                        timestamp=timeNow(),
                    )
                ]
            embeds[0].set_thumbnail(url="attachment://playerhead.png")
            
            await command_send(ctx, embeds=embeds, files=[face], ephemeral=True)
            return
        
        numServers = len(serverList)

        embed = interactions.Embed(
            title=f"{name} found",
            description=f"Found {name} in {numServers} servers",
            color=0x00FF00,
            timestamp=timeNow(),
        )
        embed.set_thumbnail(url="attachment://playerhead.png")

        await command_send(ctx, embeds=[embed], files=[face])
        
        search = {"lastOnlinePlayersList": {"$elemMatch": {"uuid": uuid}}}  # search for player

    if search == {} and not flag:
        await command_send(
            ctx,
            embeds=[
                interactions.Embed(
                    title="Error", description="No search parameters given", color=0xFF6347, timestamp=timeNow()
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
                serverList = fncs._find(search)

                numServers = len(serverList)
            else:
                fncs.dprint("Flag is up, setting server info")
                numServers = len(serverList)

            fncs.dprint(f"Servers:{len(serverList)}|Search:{search}|Flag:{flag}")
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

            # setup the embed
            embed = fncs.genEmbed(serverList, search)
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

        host = msg.embeds[0].title[
            2:  # exclude the online symbol
        ]

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
                    name=("🟢 "if player["online"] else "🔴 ")+player["name"],
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
        
        await ctx.defer(edit_origin=True)
        
        await component_edit(
            ctx,
            embeds=[
                interactions.Embed(
                    title="Loading...",
                    description="Loading the next server...",
                    color=0x00FF00,
                    timestamp=timeNow(),
                )
            ],
        )
        
        text = msg.footer.text
        # fncs.dprint("Getting footer: "+text)
        text = text.split("\n")[2]
        text = text.split("Key:")[1]
        text = text.split("/|\\")
        key = text[0]
        index = int(text[1])
        
        key = json.loads(key) if key != "---n/a---" else {}

        fncs.dprint("ReGenerating list")
        serverList = fncs._find(key)
        fncs.dprint("List generated: "+str(len(serverList))+" servers")

        embed = fncs.genEmbed(_serverList=serverList, search=key, index=index)
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
            embeds=[interactions.Embed(title="Stats", description="Getting stats...", timestamp=timeNow())]
        )

        fncs.dprint("Getting stats...")

        serverCount = col.count_documents({})
        # add commas to server count
        serverCount = "{:,}".format(serverCount)
        text = f"Total servers: `{serverCount}`\nPlayer Count: `...`\nPlayers logged: `...`\nMost common version:\n`...`"
        await ctx.edit(embeds=[interactions.Embed(title="Stats", description=text, timestamp=timeNow())])

        fncs.dprint("Getting versions...")
        versions = fncs.get_sorted_versions(col)
        topTen = [x["version"] for x in versions[:10]]

        text = "Total servers: `{}`\nRough Player Count: `...`\nMost common version:```css\n{}\n```".format(
            serverCount, ("\n".join(topTen[:5]))
        )
        await ctx.edit(embeds=[interactions.Embed(title="Stats", description=text, timestamp=timeNow())])

        fncs.dprint("Getting player count...")
        players = fncs.get_total_players_online(col)
        # add commas to player count
        players = "{:,}".format(players)
        
        fncs.dprint("Getting players logged...")
        pLogged = fncs.getPlayersLogged(col)
        pLogged = "{:,}".format(pLogged)
        text = "Total servers: `{}`\nRough Player Count: `{}`\nPlayers logged: `{}`\nMost common version:```css\n{}\n```".format(
            serverCount, players, pLogged, ("\n".join(topTen[:5]))
        )

        print(
            f"Total servers: {serverCount}\nRough Player Count: {pLogged}/{players}\nMost common versions: {topTen}"
        )

        await ctx.edit(embeds=[interactions.Embed(title="Stats", description=text, timestamp=timeNow())])
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
    *Returns:*
        `(desc, db _id, players, version, ping, players online, last online (y/m/d h:m:s))`
        
`/stats` - Get stats about the database

`/help` - Get help
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
