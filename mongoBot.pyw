import base64
from io import BytesIO
import interactions
import os
import sys
import pymongo
import mcstatus
from funcs import funcs
import time
import re
import discord

try:
    from privVars import *
except ImportError:
    MONGO_URL = "mongodb+srv://..."
    TOKEN = "..."

# Setup
# ---------------------------------------------

bot = interactions.Client(token=TOKEN)  # type: ignore

client = pymongo.MongoClient(MONGO_URL, server_api=pymongo.server_api.ServerApi("1"))  # type: ignore

db = client["mc"]
col = db["servers"]

fncs = funcs()

# Funcs
# ---------------------------------------------

def check(host):
    """Checks out a host and adds it to the database if it's not there

    Args:
        host (String): ip of the server

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
                    "lastOnlineFavicon":"base64 encoded image"
                }
    """
    
    try:
        import re

        server = mcstatus.JavaServer.lookup(host)
            
        description = server.status().description
        description = re.sub(r"§\S*[|]*\s*", "", description)

        if server.status().players.sample is not None:
            players = list(i.name for i in server.status().players.sample) # type: ignore
        else:
            players = []

        data = {
            "host": host,
            "lastOnline": time.time(),
            "lastOnlinePlayers": server.status().players.online,
            "lastOnlineVersion": str(server.status().version.name),
            "lastOnlineDescription": str(description),
            "lastOnlinePing": int(server.status().latency * 10),
            "lastOnlinePlayersList": players,
            "lastOnlinePlayersMax": server.status().players.max,
            "lastOnlineVersionProtocol": str(server.status().version.protocol),
            "favicon": server.status().favicon if server.status().favicon else None,
        }

        if not col.find_one({"host": host}):
            print("Server not in database, adding...")
            col.insert_one(data)

        return data
    except Exception as e:
        print("\r", e, " | ", host, end="\r")
        return None

def remove_duplicates():
    for i in col.find():
        if col.count_documents({"host": i["host"]}) > 1:
            col.delete_one({"_id": i["_id"]})

# Commands
# ---------------------------------------------
"""
{
  "_id":"hex value",
  "host":"ipv4 addr",
  "lastOnline":"unicode time",
  "lastOnlinePlayers": int,
  "lastOnlineVersion":"Name Version",
  "lastOnlineDescription":"Very Good Server",
  "lastOnlinePing":"unicode time",
  "lastOnlinePlayersList":["Notch","Jeb"],
  "lastOnlinePlayersMax": int,
  "lastOnlineFavicon":"base64 encoded image"
}
"""


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
            description="The player to search for",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="version",
            description="The version of the server",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def find(ctx: interactions.CommandContext, _id: str = None, Player: str = None, version: str = None, host: str = None, port: int = 25565): # type: ignore
    """Find a server

    Args:
        _id (str, optional): The ID of the server. Defaults to None.
        host (str, optional): The host of the server. Defaults to None.
        Player (str, optional): The player to search for. Defaults to None.
        version (str, optional): The version of the server. Defaults to None.
    """

    print("find", _id, host, port, Player, version)
    await ctx.defer()
    # await ctx.send("Searching...")
    # send as embed
    await ctx.send(embeds=[interactions.Embed(title="Searching...", description="Searching...")])

    info = ""
    if _id:
        info = (col.find_one({'_id': _id}) if col.find_one({'_id':_id}) else "Server not found")
    elif host:
        if col.find_one({'host': host}):
            info = (col.find_one({'host': host}))
        else:
            info = check(host+":"+str(port))
    elif Player:
        serverList = col.find()
        
        for server in serverList:
            if Player in server["lastOnlinePlayersList"]:
                info = (server)
                break
    elif version:
        serverList = col.find()
        
        for server in serverList:
            if version in server["lastOnlineVersion"]:
                info = (server)
                break
    elif Player:
        serverList = col.find()
        
        for server in serverList:
            if Player in server["lastOnlinePlayersList"]:
                info = (server)
                break
    elif version:
        serverList = col.find()
        
        for server in serverList:
            if version in server["lastOnlineVersion"]:
                info = (server)
                break
    elif Player:
        serverList = col.find()
        
        for server in serverList:
            if Player in server["lastOnlinePlayersList"]:
                info = (server)
                break
    else:
        info = {"host": "No search parameters given.", "lastOnlinePlayers": -1, "lastOnlineVersion": -1, "lastOnlineDescription": "No search parameters given.", "lastOnlinePing": -1}

    if info or str(type(info)) == 'str':
        try:
            try:
                server = mcstatus.JavaServer.lookup(info["host"]) # type: ignore
                players = list(i.name for i in server.status().players.sample) # type: ignore
            except:
                players = info["lastOnlinePlayersList"] # type: ignore
                
            # await ctx.edit(f'Host: `{info["host"]}`\nPlayers Online: `{info["lastOnlinePlayers"]}`\nVersion: {info["lastOnlineVersion"]}\nDescription: {info["lastOnlineDescription"]}\nPing: `{str(info["lastOnlinePing"])}ms`\nPlayers: {str(players)}') # type: ignore
            await ctx.edit(embeds=[interactions.Embed(title="Server Info", description=f'Host: `{info["host"]}`\nPlayers Online: `{info["lastOnlinePlayers"]}`\nVersion: {info["lastOnlineVersion"]}\nDescription: {info["lastOnlineDescription"]}\nPing: `{str(info["lastOnlinePing"])}ms`\nPlayers: {str(players)}')]) # type: ignore
        except Exception as e:
            print(f"====\nError: {e}\n----\n{type(info)}\n----\n{info}\n====")
            fncs.log(f"Error: {e}")
            await ctx.send("Error finding server, check the console and log for more info.")
            
    else:
        await ctx.send("Server not found")


    import threading;threading.Thread(target=remove_duplicates).start();print("Duplicates removed")


@bot.command(
    name='stats',
    description='Get stats about the database',
)
async def stats(ctx: interactions.CommandContext): # type: ignore
    await ctx.defer()
    try:
        """Get stats about the database"""
        fncs.log(f"stats()")
        players = 0
        for i in col.find():
            players += i["lastOnlinePlayers"]
        serverCount = col.count_documents({})

        text = f"Total servers: `{serverCount}`\nTotal players: `{players}`\nMost common version: `...`"
        
        await ctx.send(embeds=[interactions.Embed(title="Stats", description=text)]) # type: ignore
        print("Getting most common version...")

        versions = []

        for i in col.find():
            if i["lastOnlineVersion"] not in versions:
                vers = i["lastOnlineVersion"]
                # remove all non numbers or non dots
                vers = re.sub(r"[^0-9.]", "", vers)

                versions.append(vers)
        mostComVersion = ""
        for i in versions:
            if col.count_documents({"lastOnlineVersion": i}) > col.count_documents({"lastOnlineVersion": mostComVersion}):
                mostComVersion = i

        print(f"Total servers: `{serverCount}`\nTotal players: `{players}`\nMost common version: `{mostComVersion}`")

        # edit the message
        text = f"Total servers: `{serverCount}`\nTotal players: `{players}`\nMost common version: `{mostComVersion}`"
        
        await ctx.edit(embeds=[interactions.Embed(title="Stats", description=text)]) # type: ignore
    except Exception as e:
        print(f"====\nError: {e}\n====")
        fncs.log(f"Error: {e}")
        
        await ctx.send(embeds=[interactions.Embed(title="Error", description="Error getting stats, check the console and log for more info.")]) # type: ignore

    import threading;threading.Thread(target=remove_duplicates).start();print("Duplicates removed")


@bot.command(
    name="restart"
)
async def restart(ctx: interactions.CommandContext): # type: ignore
    """Restart the bot"""
    fncs.log(f"restart()")
    await ctx.send("Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.command(
    name="help"
)
async def help(ctx: interactions.CommandContext): # type: ignore
    """Get help"""
    fncs.log(f"help()")
    await ctx.send(embeds=[interactions.Embed(title="Help", description="""Commands: \nfind - Find a server\nstats - Get stats about the database\nrestart - Restart the bot\nhelp - Get help\n""")])

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
                fncs.log(e)
                time.sleep(5)
                break
