import pymongo
import traceback
import time
import threading
import random
import multiprocessing
import multiprocessing.pool
import asyncio
import funcs
useWebHook = None
try:
    from privVars import *
except ImportError:
    MONGO_URL = "mongodb+srv://..."
    DSICORD_WEBHOOK = "discord.api.com/..."

# Setup
# ---------------------------------------------

if useWebHook is None:
    useWebHook = False
    # whether to use discord webhooks or not when a server is found

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

fncs = funcs.funcs(collection=col)

# Funcs
# ---------------------------------------------
def check(host):
    if useWebHook:
        return fncs.check(host, webhook=DSICORD_WEBHOOK)
    else:
        return fncs.check(host)

def scan(ip_list):
    try:
        import masscan # type: ignore
        import json

        scanner = masscan.PortScanner()
        scanner.scan(
            ip_list,
            ports="25565",
            arguments="--max-rate {}".format(pingsPerSec / maxActive),
            sudo=True,
        )
        res = json.loads(scanner.scan_result) # type: ignore
        print(scanner.scan_result)

        return list(res["scan"].keys())
    except Exception:
        Eprint(traceback.format_exc())
        return []

def Eprint(text):
    """Error printer

    Args:
        text (String): Error text
    """
    text = str(text)
    disLog("Error: "+"".join(str(i) for i in text))
    fncs.dprint("\n"+"".join(str(i) for i in text)+"\n")


def disLog(text, end="\r"):
    try:
        import requests

        url = DSICORD_WEBHOOK
        data = {"content": text + end}
        requests.post(url, data=data)
    except Exception:
        Eprint(text+'\n'+traceback.format_exc())
        pass

async def threader(ip_range):
    try:
        ips = scan(ip_range)

        for ip in ips: # type: ignore
            check(ip)
    except Exception:
        Eprint(traceback.format_exc())

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

#ip_lists = ip_lists[:500]  # remove for final version
print(ip_lists[0:1])
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
