import pymongo
import mcstatus
from funcs import funcs
import time
import threading
import random
import multiprocessing
import multiprocessing.pool
import asyncio

try:
    from privVars import *
except ImportError:
    MONGO_URL = "mongodb+srv://..."
    TOKEN = "..."
    DSICORD_WEBHOOK = "discord.api.com/..."

# Setup
# ---------------------------------------------

pingsPerSec = 2400
maxActive = 5
DEBUG = True
time_start = time.time()
upHosts = []
results = []
res = []
threads = []
pool = multiprocessing.pool.ThreadPool(maxActive)
c = 0

client = pymongo.MongoClient(MONGO_URL, server_api=pymongo.server_api.ServerApi("1"))  # type: ignore
db = client["mc"]
col = db["servers"]
fncs = funcs()

# Funcs
# ---------------------------------------------

def check(host):
    try:
        import mcstatus
        import re

        print("\r", end="")
        server = mcstatus.JavaServer.lookup(host)
        status = server.status()
        description = status.description
        # remove color codes and whitespace
        description = description = re.sub(r"§\S*[|]*\s*", "", description)

        return host, status, description
    except Exception as err:
        return None

def scan(ip_list):
    try:
        import masscan
        import json

        scanner = masscan.PortScanner()
        scanner.scan(
            ip_list,
            ports="25565",
            arguments="--max-rate {}".format(pingsPerSec / maxActive),
        )
        res = json.loads(scanner.scan_result) # type: ignore
 
        return list(res["scan"].keys())
    except Exception as e:
        Eprint(e)

def dprint(text, end="\r"):
    """Debugging print

    Args:
        text (string): text to output
        end (str, optional): end of print statement. Defaults to "\r".
    """
    if DEBUG:
        print(text, end=end)

def Eprint(text):
    """Error printer

    Args:
        text (String): Error text
    """
    fncs.log("Error: "+"".join(str(i) for i in text))
    dprint("\n"+"".join(str(i) for i in text)+"\n")


def disLog(text, end="\r"):
    try:
        import requests

        url = DSICORD_WEBHOOK
        data = {"content": text + end}
        requests.post(url, data=data)
    except Exception:
        Eprint(text)
        pass

def add(host):
    if not col.find_one({"host": host}):
        try:
            import re

            server = mcstatus.JavaServer.lookup(host)

            description = server.status().description
            description = re.sub(r"§\S*[|]*\s*", "", description)

            if server.status().players.sample is not None:
                players = [player.name for player in server.status().players.sample] # type: ignore
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

            col.insert_one(data)
            print(f"\nadded {host}\n")
            disLog(f"added {host}")
        except Exception as e:
            Eprint(("\r"+e+" | "+host)) # type: ignore

async def threader(ip_range):
    try:
        ips = scan(ip_range)

        for ip in ips: # type: ignore
            res = check(ip)
            if res is not None:
                add(res[0])
    except Exception as e:
        Eprint(e)

def crank(ip_range):
    asyncio.run(threader(ip_range))

# Main
# ---------------------------------------------

# create a list of ipv4 ranges
ip_lists = []
for i in range(255):
    for j in range(255):
        ip_lists.append(f"{i}.{j}.0.0/16")
random.shuffle(ip_lists)

ip_lists = ip_lists[:50]  # remove for final version
time.sleep(0.5)

normal = threading.active_count()
async def makeThreads():
    # create threads
    threads = []
    # Create a thread for each list of IPs
    for ip_list in ip_lists:
        # Create the thread
        t = threading.Thread(target=crank, args=(ip_list,),name=f"Scan func thread: {ip_list}")
        # Add the thread to the list of threads
        threads.append(t)
        # If the number of active threads is greater than the max, sleep for 0.1 seconds
        while threading.active_count()-normal >= maxActive:
            await asyncio.sleep(0.1)
        t.start()

        print(f"\rstarted proc for {ip_list} | {threading.active_count()-normal}/{maxActive} active threads, #{ip_lists.index(ip_list)+1} {' '*10}", end="\r")


asyncio.run(makeThreads())

# print results
print(f"\nfinished in {round(time.time() - time_start, 2)}s")
