# pyright: basic
import multiprocessing
import sys
import time
import traceback
import base64
import re
import threading
import random
from xmlrpc.client import Server
import requests
import json
import chat

import pymongo
from bson.objectid import ObjectId
import mcstatus
import interactions
from interactions.ext.files import command_edit, component_edit, command_send, component_send

from funcs import funcs

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

bot = interactions.Client(token=TOKEN)

client = pymongo.MongoClient(MONGO_URL, server_api=pymongo.server_api.ServerApi("1")) # pyright: ignore [reportGeneralTypeIssues=false]

db = client["mc"]
col = db["servers"]
serverList = []
ServerInfo = {}
_port = "25565"

fncs = funcs(collection=col)


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
            description="The player to search for **WIP**",
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
        )
    ],
)
async def find(ctx: interactions.CommandContext, _id: str = "", player: str = "", version: str = "", host: str = "", port: int = 25565, motd: str = "", maxplayers: int = -1, cracked: bool = False):  
    """Find a server

    Args:
        _id (str, optional): The ID of the server. Defaults to None.
        host (str, optional): The host of the server. Defaults to None.
        Player (str, optional): The player to search for. Defaults to None.
        version (str, optional): The version of the server. Defaults to None.
        motd (str, optional): The motd of the server. Defaults to None.
        port (int, optional): The port of the server. Defaults to 25565.
    """

    print("find", _id, host, port, player, version, motd, maxplayers)
    fncs.log("find", _id, host, port, player, version, motd, maxplayers)
    
    # send as embed
    await ctx.defer()

    global _port
    search = {}
    info = {}
    _port = port
    flag = False
    # if parameters are given, add them to the search

    if host:
        search["host"] = host.lower()
        fncs.check(host, str(port))
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
        info = col.find_one({"_id": ObjectId(_id)})
        flag = True
        fncs.dprint("Finding id", _id)
    if player:
        search = {}
        flag = True
        url = "https://api.mojang.com/users/profiles/minecraft/"
        
        # check if player is valid or if the input is a uuid
        resp = requests.get(url+player)
        print(resp.text)

        if resp.status_code == 204 and resp.text == "":
            resp = requests.get("https://sessionserver.mojang.com/session/minecraft/profile/"+player.replace("-","")); jresp = resp.json()
            if 'error' in resp.text or resp.text == "":
                fncs.dprint("Player not found in minecraft api")
                await command_send(ctx, embeds=[interactions.Embed(title="Error",description="Player not found in minecraft api")])
                return
            else:
                player = jresp['id']
        else:
            try:
                player = resp.json()['id']
            except Exception:
                fncs.dprint("Player not found in minecraft api")
                await command_send(ctx, embeds=[interactions.Embed(title="Error",description="Player not found in minecraft api",color=0xFF6347)])
                return


        info = col.find_one({"lastOnlinePlayersList": {"$elemMatch": {"uuid": player}}})
        fncs.dprint("Finding player", player)

        if not info:
            fncs.dprint("Player not found in database")
            await command_send(ctx, embeds=[interactions.Embed(title="Error",description="Player not found in database",color=0xFF6347)])
            return

    if search == {} and not flag:
        await command_send(ctx, embeds=[interactions.Embed(title="Error",description="No search parameters given")])
    else:
        try:
            global _serverList
            global ServerInfo
            
            if not flag:
                _serverList = []
                _info_ = fncs._find(search, port=str(port), serverList=serverList)

                _serverList = list(_info_[0]) # pyright: ignore [reportGeneralTypeIssues]
                # remove duplicates from _serverList
                _serverList = [i for n, i in enumerate(_serverList) if i not in _serverList[n + 1:]]
                numServers = len(_serverList) 
            else:
                fncs.dprint("Flag is up, setting server info to", info)
                ServerInfo = info
                _serverList = [info]
                numServers = 1

            fncs.dprint(len(_serverList),search)
            

            await command_send(ctx, embeds=[interactions.Embed(title="Searching...",description="Sorting through "+str(numServers)+" servers...")])

            # setup the embed
            embed = fncs.genEmbed(_serverList, str(_port))
            _file = embed[1]
            comps = embed[2]
            ServerInfo = embed[3] if ServerInfo == {} else ServerInfo
            embed = embed[0]
            

            fncs.dprint("Embed generated",embed, comps, _file)

            
            
            # send the embed sometimes with the favicon
            if _file: 
                await command_edit(ctx, embeds=[embed], files=[_file], components=comps) 
            else:
                await command_edit(ctx, embeds=[embed], components=comps) # pyright: ignore [reportGeneralTypeIssues]
        except Exception:
            fncs.log(traceback.format_exc())
            await command_send(ctx, embeds=[interactions.Embed(title="Error", description="An error occured while searching. Please try again later and check the logs for more details.", color=0xFF0000)])
            print(f"----\n{traceback.format_exc()}\n====\n{type(info)}\n====\n{info}\n====\n====\n{ServerInfo}\n====\n----") 


    threading.Thread(target=fncs.remove_duplicates).start();fncs.dprint("Duplicates removed")


@bot.component("show_players")
async def show_players(ctx: interactions.ComponentContext):  
    try:
        await ctx.defer()

        # get current message

        global ServerInfo
        info = ServerInfo

        players = list(info["lastOnlinePlayersList"])
        random.shuffle(players) # for servers with more than 25 logged players

        embed = interactions.Embed(
            title="Players", 
            description="{} players logged".format(len(players)),
        )

        for player in players:
            try:
                if str(player).startswith("{"):
                    # player is dict type
                    player = json.loads(str(player).replace("'", '"'))
                    embed.add_field(name=player["name"], value="`{}`".format(player["uuid"]), inline=True)
                else:
                    # player is str type
                    embed.add_field(name=player, value="`{}`".format(player), inline=True)
            except Exception:
                print(traceback.format_exc())
                print(player)
                break

        fncs.dprint(embed, "\n---\n", players)

        await component_send(ctx, embeds=[embed], ephemeral=True)
    except Exception:
        print(traceback.format_exc())
        await component_send(ctx, embeds=[interactions.Embed(title="Error", description="An error occured while searching. Please try again later and check the logs for more details.", color=0xFF0000)], ephemeral=True)

    threading.Thread(target=fncs.remove_duplicates).start();fncs.dprint("Duplicates removed")

@bot.component("rand_select")
async def rand_select(ctx: interactions.ComponentContext):
    await ctx.defer(edit_origin=True)
    
    global _serverList

    embed = fncs.genEmbed(_serverList, _port)
    _file = embed[1]
    button = embed[2]
    embed = embed[0]

    fncs.dprint("Embed generated",embed, button, _file)

    if _file:
        await component_edit(ctx, embeds=[embed], files=[_file], components=button)
    else:
        await component_edit(ctx, embeds=[embed], components=button)

    threading.Thread(target=fncs.remove_duplicates).start();fncs.dprint("Duplicates removed")



@bot.command(
    name="stats",
    description="Get stats about the database",
)
async def stats(ctx: interactions.CommandContext):  
    await ctx.defer()
    try:
        """Get stats about the database"""
        players = 0
        for i in col.find():
            players += i["lastOnlinePlayers"]
        serverCount = col.count_documents({})

        text = f"Total servers: `{serverCount}`\nTotal players: `{players}`\nMost common version: `...`"

        await ctx.send(embeds=[interactions.Embed(title="Stats", description=text)])  
        print("Getting most common version...")

        versions = []

        for i in col.find():
            versions.append(i["lastOnlineVersion"])

        versions.sort(key=versions.count, reverse=True)


        print(
            f"Total servers: {serverCount}\nTotal players: {players}\nMost common version: {str(versions[0:10])[1:-1]}"
        )

        # edit the message
        text = "Total servers: `{}`\nTotal players: `{}`\nMost common version:\n```{}```".format(serverCount,players,('\n'.join(versions[0:5])))

        await ctx.edit(embeds=[interactions.Embed(title="Stats", description=text)])  
    except Exception:
        print(f"====\nError: {traceback.format_exc()}\n====")
        fncs.log(traceback.format_exc())

        await ctx.send(embeds=[interactions.Embed(title="Error", description="Error getting stats, check the console and log for more info.")])  


    threading.Thread(target=fncs.remove_duplicates).start();fncs.dprint("Duplicates removed")



@bot.command(name="help")
async def help(ctx: interactions.CommandContext):  
    """Get help"""
    await ctx.send(
        embeds=[
            interactions.Embed(
                title="Help",
                description="""Commands: \n`/find` - Find a server\n*Returns:*\n`    (desc, db _id, players, version, ping, players online, last online (y/m/d h:m:s))`\n`/stats` - Get stats about the database\n`/restart` - Restart the bot\n`/help` - Get help\n""",
            )
        ]
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
                fncs.log(traceback.format_exc())
                time.sleep(30)
                break
