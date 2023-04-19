import asyncio
import json
import multiprocessing
import multiprocessing.pool
import random
import sys
import threading
import time
import traceback

import masscan as msCan
import pymongo

import utils

useWebHook, pingsPerSec, maxActive = False, 4800, 10
masscan_search_path = (
    "masscan",
    "/usr/bin/masscan",
    "/usr/local/bin/masscan",
    "/sw/bin/masscan",
    "/opt/local/bin/masscan",
)
DISCORD_WEBHOOK = "discord.api.com/..."
try:
    from privVars import *
except ImportError:
    MONGO_URL = "mongodb+srv://..."
    DSICORD_WEBHOOK = "discord.api.com/..."


if MONGO_URL == "mongodb+srv://...":
    print("Please add your mongo url to privVars.py")
    input()
    sys.exit()
if useWebHook and DISCORD_WEBHOOK == "discord.api.com/...":
    print("Please add your discord webhook to privVars.py")
    input()
    sys.exit()

# Setup
# ---------------------------------------------

DEBUG = True

time_start = time.time()
threads = []
pool = multiprocessing.pool.ThreadPool(maxActive)

client = pymongo.MongoClient(
    MONGO_URL, server_api=pymongo.server_api.ServerApi("1")
)  # type: ignore
db = client["mc"]
col = db["servers"]

utils = utils.utils(col, debug=DEBUG)
logger = utils.logger
finder = utils.finder

# Funcs
# ---------------------------------------------


def print(*args, **kwargs):
    logger.print(*args, **kwargs)


def check(scannedHost):
    # example host: "127.0.0.1": [{"status": "open", "port": 25565, "proto": "tcp"}]

    try:
        if scannedHost.replace(".").isdigit():
            ip = scannedHost
        else:
            ip = list(scannedHost.keys())[0]
    except Exception:
        logger.print("Error parsing host: " + str(scannedHost))
        logger.error(traceback.format_exc())
        return

    portsJson = (
        scannedHost[ip]
        if not isinstance(scannedHost, str)
        else [{"status": "open", "port": 25565, "proto": "tcp"}]
    )
    for portJson in portsJson:
        if portJson["status"] == "open":
            if useWebHook:
                return finder.check(
                    host=str(ip) + ":" + str(portJson["port"]), webhook=DISCORD_WEBHOOK
                )
            else:
                return finder.check(host=str(ip) + ":" + str(portJson["port"]))
    else:
        return


def scan(ip_list):
    try:
        scanner = msCan.PortScanner(masscan_search_path=masscan_search_path)
    except msCan.PortScannerError:
        print("Masscan not found, please install it")
        return []

    try:
        import json

        scanner.scan(
            ip_list,
            ports="25565-25577",
            arguments="--max-rate {}".format(pingsPerSec / maxActive),
            sudo=True,
        )
        result = json.loads(scanner.scan_result)

        return list(result["scan"])
    except OSError:
        sys.exit(0)
    except Exception:
        logger.error(traceback.format_exc())
        return []


def disLog(text, end="\r"):
    if useWebHook:
        try:
            import requests

            url = DSICORD_WEBHOOK
            data = {"content": text + end}
            requests.post(url, data=data)
        except Exception:
            logger.error(text + "\n" + traceback.format_exc())


async def threader(ip_range):
    try:
        ips = scan(ip_range)

        if len(ips) > 0:
            pool = multiprocessing.pool.ThreadPool(maxActive // 2)
            pool.map(check, ips)
    except OSError:
        sys.exit(0)
    except Exception:
        logger.error(traceback.format_exc())


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

ip_lists = ip_lists[:1000]  # remove for final version
time.sleep(0.5)

tStart = time.time()
normal = threading.active_count()


async def makeThreads():
    # Create a thread for each list of IPs
    for ip_list in ip_lists:
        # check to make sure that more than 2*maxActive threads haven't been created in the last 1 second
        if len(threads) >= maxActive * 2 and time.time() - tStart <= 1:
            await asyncio.sleep(0.5)
            logger.error(
                "Too many threads spawned to quickly, exiting\nPlease check the console and logs for more details"
            )
            sys.exit()

        t = threading.Thread(
            target=crank, args=(ip_list,), name=f"Scan func thread: {ip_list}"
        )

        threads.append(t)

        # If the number of active threads is greater than the max, sleep for 0.1 seconds
        while threading.active_count() - normal >= maxActive:
            await asyncio.sleep(0.1)
        t.start()


if __name__ == "__main__":
    asyncio.run(makeThreads())
