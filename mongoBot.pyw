import interactions
import os
import sys
import pymongo
import mcstatus
from funcs import funcs
import time

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
    """_summary_

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
        }

        if not col.find_one({"host": host}):
            print("Server not in database, adding...")
            col.insert_one(data)

        return data
    except Exception as e:
        print("\r", e, " | ", host, end="\r")
        pass
    finally:        
        import threading
        # remove dulpicate hosts in pymongo
        def remove_duplicates():
            for i in col.find():
                if col.count_documents({"host": i["host"]}) > 1:
                    col.delete_one({"_id": i["_id"]})

        threading.Thread(target=remove_duplicates).start()
        print("Done")

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
            type=interactions.OptionType.STRING,
            description="The host of the server",
            required=False,
        ),
        interactions.Option(
            name="player",
            description="The player to search for",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def find(ctx: interactions.CommandContext, _id: str = None, host: str = None, Player: str = None): # type: ignore
    """Find a server

    Args:
        _id (str, optional): The ID of the server. Defaults to None.
        host (str, optional): The host of the server. Defaults to None.
        Player (str, optional): The player to search for. Defaults to None.
    """
    fncs.log(f"find({_id}, {host or Player})")
    if _id:
        await ctx.send(col.find_one({'_id': _id}) if col.find_one({'_id':_id}) else "Server not found")
    elif host:
        await ctx.send(col.find_one({"host": host}) if col.find_one({"host": host}) else "Server not found")
    elif Player:
        serverList = col.find()
        
        for server in serverList:
            if Player in server["lastOnlinePlayersList"]:
                await ctx.send(server)

@bot.command(
    name="status",
    description="Get the status of a server",
    options=[
        interactions.Option(
            name="host",
            type=interactions.OptionType.STRING,
            description="The host of the server",
            required=True,
        ),
    ],
)
async def status(ctx: interactions.CommandContext, host: str): # type: ignore
    """Get the status of a server"""
    fncs.log(f"status({host})")
    info = check(host)
    if info:
        await ctx.send(f"```{info}```")
    else:
        await ctx.send("Server is offline")

@bot.command(
    name="add",
    description="Add a server",
    options=[
        interactions.Option(
            name="host",
            type=interactions.OptionType.STRING,
            description="The host of the server",
            required=True,
        ),
    ],
)
async def add(ctx: interactions.CommandContext, host: str): # type: ignore
    """Add a server"""
    fncs.log(f"add({host})")
    await ctx.send(f"```{check(host)}```")

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
    await ctx.send("```Commands: find, status, add, restart, help```")

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