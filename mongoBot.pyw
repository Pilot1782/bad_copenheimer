import base64
from io import BytesIO
import interactions
import os
import sys
import pymongo
import mcstatus
from funcs import funcs
import time
import discord
from PIL import Image

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

fncs = funcs(os.path.dirname(os.path.abspath(__file__)))

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
        interactions.Option(
            name="version",
            description="The version of the server",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ],
)
async def find(ctx: interactions.CommandContext, _id: str = None, host: str = None, Player: str = None, version: str = None): # type: ignore
    """Find a server

    Args:
        _id (str, optional): The ID of the server. Defaults to None.
        host (str, optional): The host of the server. Defaults to None.
        Player (str, optional): The player to search for. Defaults to None.
        version (str, optional): The version of the server. Defaults to None.
    """

    print("find", _id, host, Player, version)

    info = ""
    if _id:
        info = (col.find_one({'_id': _id}) if col.find_one({'_id':_id}) else "Server not found")
    elif host:
        info = (col.find_one({"host": host}) if col.find_one({"host": host}) else None)
        info = (check(host) if info is None else "Server not found")
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
        info = "Server not found"

    if info or info != "Server not found":
        try:
            text = f'Host: `{info["host"]}`\nPlayers Online: `{info["lastOnlinePlayers"]}`\nVersion: {info["lastOnlineVersion"]}\nDescription: {info["lastOnlineDescription"]}\nPing: `{info["lastOnlinePing"]}ms`' # type: ignore
            await ctx.send(f"{text}")
            img = base64.b64decode((mcstatus.JavaServer.lookup(host).status().favicon).split(",")[1]) # type: ignore
            with open(r"{}images{}.png".format(("/" if os.name != "nt" else "\\"),host), "wb") as fp:
                fp.write(img)
            with open(r"{}images{}.png".format(("/" if os.name != "nt" else "\\"),host), "rb") as fh:
                f = discord.File(fh, filename=f"{host}.png")
            # await ctx.send(file=f)
        except Exception as e:
            print(e)
            print(info)
            await ctx.send("Server not found")
            fncs.log(f"Error: {e}")
    else:
        await ctx.send("Server not found")


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
    await ctx.send("""Commands:
find - Find a server
restart - Restart the bot
help - Get help
""")

# Run the bot
# ---------------------------------------------
                
def rest():
    import time
    # sleep for 2 hours then restart
    print("Restarting in 2 hours")
    time.sleep(7200)
    os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    while True:
        try:
            import threading
            threading.Thread(target=rest).start()

            bot.start()
        except Exception as e:
            if e == KeyboardInterrupt:
                break
            else:
                print(e)
                fncs.log(e)
                time.sleep(5)
                break
