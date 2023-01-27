import base64
import builtins
import twisted, quarry
import random
import re
import subprocess
import json
import time
import os as osys
import traceback
import interactions
from mcstatus import JavaServer
import mcstatus
import requests
import chat


class funcs:
    """Cursed code that I don't want to touch. It works, but it's not pretty.
        # STOP HERE

        Beyond this point is code unmaintained and at risk of mabye being important.
        Once this file was made, no proper docs on the methods have been made except those that I sometimes remember.

    """    

    def __init__(self, collection, path=osys.path.dirname(osys.path.abspath(__file__))):
        """Init the class

        Args:
            path (str, optional): Path to the directory of the folder. Defaults to os.path.dirname(os.path.abspath(__file__)).
        """

        self.path = path + ("\\" if osys.name == "nt" else "/")
        self.col = collection
        self.settings_path = self.path+(r"\settings.json" if osys.name == "nt" else "/settings.json")

        with open(
            self.settings_path, "r"
        ) as read_file:  # Open the settings file and start defineing variables from it
            global data
            data = json.load(read_file)

        # Define based on testing
        self.testing = data["testing"]  # bc it easier
        if not self.testing:
            self.TOKEN = data["TOKEN"]
            self.home_dir = data["home-dir"]
        else:
            self.TOKEN = osys.getenv("TOKEN")
            self.home_dir = osys.path.dirname(osys.path.abspath(__file__))

        self.testing = data["testing"]
        self.output_path = self.home_dir + "outputs.json"
        self.usr_name = data["user"]
        self.lower_ip_bound = data["lower_ip_bound"]
        self.upper_ip_bound = data["upper_ip_bound"]
        self.threads = data["threads"]
        self.threads = int(self.threads)
        self.timeout = data["timeout"]
        self.timeout = int(self.timeout)
        self.os = 1 if osys.name == "nt" else 0
        if self.os == 1:
            self.osp = "\\"
        else:
            self.osp = "/"
        self.mascan = data["masscan"]
        self.time2 = data["time2"]
        self.debug = data["debugging"]
        self.passwd = data["password"]
        self.server = data["server"]
        self.sport = data["server-port"]

    # Functions getting defeined

    # Write to a json file
    def write_json(self, new_data, filename="data.json"):
        with open(filename, "r+") as file:
            file_data = json.load(file)
            file_data["emp_details"].append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)

    # Print the Time
    def ptime(self):
        x = time.localtime()
        z = []
        for i in x:
            z.append(str(i))
        y = ":".join(z)
        z = f"{z[0]} {z[1]}/{z[2]} {z[3]}:{z[4]}:{z[5]}"
        return z

    # Start a python server
    def hserver(self):
        if self.server:
            osys.system("python -m http.server {0}".format(self.sport))

    # Run a command and get line by line output
    def run_command(self, command, powershell=False):
        """Just a better os.system

        Args:
            command (raw string): desired command
            powershell (bool, optional): use powershell for windows. Defaults to False.

        Returns:
            string: error message

        Yields:
            string: console output of command
        """

        if powershell:
            command = rf"C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe -command {command}"
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        # Read stdout from subprocess until the buffer is empty !
        for line in iter(p.stdout.readline, b""): # type: ignore
            if line:  # Don't print blank lines
                yield line
        # This ensures the process has completed, AND sets the 'returncode' attr
        while p.poll() is None:
            time.sleep(0.1)  # Don't waste CPU-cycles
        # Empty STDERR buffer
        err = p.stderr.read() # type: ignore
        if p.returncode != 0:
            # The run_command() function is responsible for logging STDERR
            print(str(err))
            self.log(str(err))
            return "Error: " + str(err)

    # Login into a minecraft server
    flag = False

    def login(self, host):
        for i in self.run_command(
            "python3 {4}playerlist.pyw --auth {0}:{1} -p {2} {3}".format(
                self.usr_name, self.passwd, 25565, host, self.home_dir
            )
        ):
            self.dprint(i.decode("utf-8"))
            flag = True

            return i.decode("utf-8")

    # Get the file output depending on the os
    def file_out(self):
        with open(self.output_path, "r") as f:
            data1 = json.load(f)
            for i in data1:
                return i["ip"]

    # Look through your files and see if the server you scan has 'player' playing on it, going to be redon soon
    # The redoo may be implemented but i have to test the file first.
    def find(self, player):
        """Legacy find player function, now obsolete

        Args:
            player (string): ip addr

        Returns:
            string: ip addr
        """

        outp = []
        with open(f"{self.home_dir}outputs.json", "r") as f:
            data = json.load(f)
            try:
                for i in data:
                    ip = i["ip"]
                    server = JavaServer.lookup(f"{ip}:25565")

                    status = server.status()
                    print(
                        "The server has {0} players and replied in {1} ms".format(
                            status.players.online, status.latency
                        )
                    )

                    # 'ping' is supported by all Minecraft servers that are version 1.7 or higher.
                    # It is included in a 'status' call, but is exposed separate if you do not require the additional info.
                    latency = server.ping()
                    print("The server replied in {0} ms".format(latency))

                    # 'query' has to be enabled in a servers' server.properties file.
                    # It may give more information than a ping, such as a full player list or mod information.
                    query = server.query()
                    print(
                        "The server has the following players online: {0}".format(
                            ", ".join(query.players.names)
                        )
                    )
            except:
                outp.append("Sorry, execution failed.")
            print("\n".join(outp))
            return "Done\n".join(outp)

    # Clean masscan output
    def clean(self, line):
        if "rate" in line:
            print("Skipped")
        else:
            arr = []
            words = ["Discovered", "open", "port", "25565/tcp", "on"]
            line = line.split(" ")
            for i in line:
                if i in words:
                    pass
                else:
                    arr.append(i)
            return "".join(arr)

    # Print but for debugging
    def dprint(self, *text):
        if self.debug:
            print(' '.join((str(i) for i in text)))

    # Scan to increase simplicity
    def scan(self, ipL, ipU): # dont use scan_range
        """Scan function that uses ipv4 addrs

        Args:
            ipL (ip String): lower bound
            ipU (ip String): upper bound

        Yields:
            ip String: active servers
        """

        if osys == 0 and self.mascan is True:
            command = f"sudo masscan -p25565 {ipL}-{ipU} --rate={self.threads * 3} --exclude 255.255.255.255"
            for i in self.run_command(command):
                self.dprint(i.decode("utf-8"))
                if "Discovered" in i.decode("utf-8"):
                    yield self.clean(i.decode("utf-8"))
        else:
            command = f"java -Dfile.encoding=UTF-8 -jar {self.path} -range {ipL}-{ipU} -ports 25565-25577 -th {self.threads} -ti {self.timeout}"
            for i in self.run_command(command):
                self.dprint(i.decode("utf-8"))
                if "(" in i.decode("utf-8"):
                    yield self.clean(i.decode("utf-8"))

            osys.chdir("outputs")
            files = osys.listdir(osys.getcwd())
            for i in files:
                if i.endswith(".txt"):
                    osys.remove(f"{self.home_dir}outputs\\{i}")

    # Stop command
    def halt(self):
        for line in self.run_command(f"{self.home_dir}stopper.pyw"):
            if "halt" in line:  # type: ignore
                global flag
                flag = True

    # If error then log it
    def log(self, *text):
        """Logging function

        Args:
            text (String): text to log
        
        Returns:
            None
        """
        path_ = f"{self.path}log.log"
        with open(f"{path_}", "a") as f:
            text = ' '.join((str(i) for i in text))
            f.write(f"[{self.ptime()}]{'{V2.0.0}'} {text}\n")

    # Scan a range
    def scan_range(self, ip1, ip2): #legacy verson of scan
        """Legacy Scan function

        Args:
            ip1 (ip String): lower bound
            ip2 (ip String): upper bound

        Yields:
            ip String: active servers
            string: output for discord
        """

        print("This is a legacy version of scan, use scan instead")

        yield f"Scanning started: {self.ptime()}"

        flag = False
        print(self.ptime())
        yield "Testing the Tool"
        print(f"Scanning {'172.65.238.0'}-{'172.65.240.255'}")
        arr = []
        bol = False

        if osys == 0 and self.mascan is True:
            print("testing using masscan")

            for line in self.scan("172.65.238.0", "172.65.239.0"):
                if flag:
                    break
                try:
                    self.dprint(line)
                    if "D" in line:  # type: ignore
                        bol = True
                        break
                except:
                    bol = False
            if bol:
                self.dprint("Test passed!")
                yield "Test passed!"
            else:
                self.dprint("Test failed.")
                self.log("Test failed.")
                yield "Test Failed."
        else:
            command = f"java -Dfile.encoding=UTF-8 -jar {self.path} -nooutput -range 172.65.238.0-172.65.240.255 -ports 25565-25577 -th {self.threads} -ti {self.timeout}"
            bol = False
            self.dprint(command)
            for line in list(self.scan("172.65.238.0", "172.65.240.255")):
                if flag:
                    break
                if "(" in line:  # type: ignore
                    bol = True
                    break
            if bol:
                self.dprint("Test passed!")
                yield "Test passed!"
            else:
                self.dprint("Test failed.")
                yield "Test Failed."
        yield f"\nStarting the scan at {self.ptime()}\nPinging {self.lower_ip_bound} through {self.upper_ip_bound}, using {self.threads} threads and timingout after {self.timeout} miliseconds."

        print(
            f"\nScanning on {self.lower_ip_bound} through {self.upper_ip_bound}, with {self.threads} threads and timeout of {self.timeout}"
        )

        outp = []
        if osys == 0 and self.mascan is True:
            command = f"sudo masscan -p25565 {self.lower_ip_bound}-{self.upper_ip_bound} --rate={self.threads * 3} --exclude 255.255.255.255"
            bol = False
            cnt = 0
            self.dprint(command)
            for line in self.scan(self.lower_ip_bound, self.upper_ip_bound):
                if flag:
                    break
                try:
                    if "." in line:  # type: ignore
                        bol = True
                        cnt += 1
                        arr.append(line)
                        print(line)
                        yield line
                except:
                    bol = False
            outp = arr
            self.dprint(outp)
        else:
            command = f"java -Dfile.encoding=UTF-8 -jar {self.path} -nooutput -range {self.lower_ip_bound}-{self.upper_ip_bound} -ports 25565-25577 -th {self.threads} -ti {self.timeout}"
            arr = []
            if self.debug:
                print(command)
            for line in self.scan(self.lower_ip_bound, self.upper_ip_bound):
                if flag:
                    break
                if line == "" or line is None:
                    pass
                else:
                    try:
                        if line.startswith("[") or line.startswith("("):
                            yield line
                            arr.append(line)
                    except:
                        pass
            a = []
            for i in arr:
                if i.startswith("(1") or i.startswith("(2"):
                    a.append(i)
            b = []
            for i in a:
                f = []
                for j in i:
                    if j == ":":
                        break
                    if j == "(":
                        pass
                    else:
                        f.append(j)
                b.append("".join(f))
            self.dprint("{0}\n{1}".format(b, len(b)))
            outp = b
        yield f"\nScanning finished at {self.ptime()}"
        with open(self.output_path) as fp:
            data = json.load(fp)
            for i in outp:
                bol = False
                for j in data:
                    if i in j["ip"]:
                        bol = False
                        break
                    bol = True
                if bol:
                    data.append(
                        {
                            "ip": i,
                            "timestamp": "1641565033",
                            "ports": [
                                {
                                    "port": 25565,
                                    "proto": "tcp",
                                    "status": "open",
                                    "reason": "syn-ack",
                                    "ttl": 64,
                                }
                            ],
                        }
                    )
            filename = self.output_path

            self.dprint(outp)

            with open(filename, "w") as json_file:
                json.dump(data, json_file, indent=4, separators=(",", ": "))
            self.dprint(data)
            print("Successfully appended {0} lines to the JSON file".format(len(data)))
            yield "Successfully appended {0} lines to the JSON file".format(len(data))
            self.log(
                "Successfully appended {0} lines to the JSON file".format(len(data))
            )


    def check(self,host, port="25565", webhook=None):
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
                        "cracked": bool,
                        "lastOnlineFavicon":"base64 encoded image"
                    }
        """

        try:
            server = mcstatus.JavaServer.lookup(host+":"+str(port))
            try:
                status = server.status()
            except BrokenPipeError:
                self.dprint("Broken Pipe Error")
                return None
            except ConnectionRefusedError:
                self.dprint("Connection Refused Error")
                return None
            except OSError:
                self.dprint("No Information")
                return None

            players = []
            try:
                if status.players.sample is not None:
                    for player in status.players.sample: # pyright: ignore [reportOptionalIterable]
                        url = f"https://api.mojang.com/users/profiles/minecraft/{player.name}"
                        jsonResp = requests.get(url)
                        if len(jsonResp.text) > 2:
                            jsonResp = jsonResp.json()

                            if jsonResp:
                                players.append(
                                    {
                                        "name": self.cFilter(jsonResp["name"]).lower(), # pyright: ignore [reportGeneralTypeIssues]
                                        "uuid": jsonResp["id"],
                                    }
                                )
            except Exception:
                self.log("Error getting player list", traceback.format_exc())
            

            data = {
                "host": host,
                "lastOnline": time.time(),
                "lastOnlinePlayers": status.players.online,
                "lastOnlineVersion": self.cFilter(str(re.sub(r"§\S*[|]*\s*", "", status.version.name))),
                "lastOnlineDescription": self.cFilter(str(status.description)),
                "lastOnlinePing": int(status.latency * 10),
                "lastOnlinePlayersList": players,
                "lastOnlinePlayersMax": status.players.max,
                "lastOnlineVersionProtocol": self.cFilter(str(status.version.protocol)),
                "cracked": self.crack(host, port),
                "favicon": status.favicon,
            }

            if not self.col.find_one({"host": host}):
                print("{} not in database, adding...".format(host))
                self.col.insert_one(data)
                if webhook:
                    requests.post(webhook, json={"content": f"New server added to database: {host}"})


            for i in list(self.col.find_one({"host": host})["lastOnlinePlayersList"]):
                try:
                    if i not in data["lastOnlinePlayersList"]:
                        if type(i) == str:
                            url = f"https://api.mojang.com/users/profiles/minecraft/{i}"
                            jsonResp = requests.get(url)
                            if len(jsonResp.text) > 2:
                                jsonResp = jsonResp.json()

                                if jsonResp is not None:
                                    data["lastOnlinePlayersList"].append(
                                        {
                                            "name": self.cFilter(jsonResp["name"]),
                                            "uuid": jsonResp["id"],
                                        }
                                    )
                        else:
                            data["lastOnlinePlayersList"].append(i)
                except Exception:
                    print(traceback.format_exc(), " \/ ", host) #pyright: ignore [reportInvalidStringEscapeSequence] 
                    break

            self.col.update_one({"host": host}, {"$set": data})

            return data
        except TimeoutError:
            return None
        except Exception:
            print(traceback.format_exc(), " | ", host)
            return None


    def remove_duplicates(self):
        """Removes duplicate entries in the database

        Returns:
            None
        """
        for i in self.col.find():
            if self.col.count_documents({"host": i["host"]}) > 1:
                self.col.delete_one({"_id": i["_id"]})


    def verify(self,search, serverList):
        """Verifies a search

        Args:
            search [dict], len > 0: {
                "host":"ipv4 addr",
                "lastOnline":"unicode time",
                "lastOnlinePlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePing":"unicode time",
                "lastOnlinePlayersList":["Notch","Jeb"],
                "lastOnlinePlayersMax": int,
                "favicon":"base64 encoded image"
            }
            serverList [list], len > 0: {
                "host":"ipv4 addr", # optional
                "lastOnline":"unicode time", # optional
                "lastOnlinePlayers": int, # optional
                "lastOnlineVersion":"Name Version", # optional
                "lastOnlineDescription":"Very Good Server", # optional
                "lastOnlinePing":"unicode time", # optional
                "lastOnlinePlayersList":["Notch","Jeb"], # optional
                "lastOnlinePlayersMax": int, # optional
                "favicon":"base64 encoded image" # optional
            }

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
                "favicon":"base64 encoded image"
            }
        """
        out = []
        _items = list(search.items())
        for server in serverList:
            flag = True
            for _item in _items:
                key = str(_item[0])
                value = str(_item[1])
                if key in server:
                    if str(value).lower() not in str(server[key]).lower():
                        flag = False
                        break
            if flag:
                out.append(server)
                
        print(str(len(out)) + " servers match")

        random.shuffle(out);return out

    def _find(self, search, serverList, port="25565"):
        """Finds a server in the database

        Args:
            search [dict], len > 0: {
                "host":"ipv4 addr",
                "lastOnlineMaxPlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePlayersList": ["WIP", "WIP"],
            }

        Returns:
            [dict]: {
                "host":"ipv4 addr",
                "lastOnline":"unicode time",
                "lastOnlinePlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePing":"unicode time",
            }
        """
        # find the server given the parameters
        if search != {}:
            servers = list(self.col.find())
        else:
            return {
                "host": "Server not found",
                "lastOnline": 0,
                "lastOnlinePlayers": -1,
                "lastOnlineVersion": "Server not found",
                "lastOnlineDescription": "Server not found",
                "lastOnlinePing": -1,
                "lastOnlinePlayersList": [],
                "lastOnlinePlayersMax": -1,
                "favicon": "Server not found"
            }


        for server in servers:
            _items = list(search.items())
            try:
                for _item in _items:
                    if _item[0] in server:
                        if str(_item[1]).lower() in str(server[_item[0]]).lower():
                            serverList.append(server)
                            break
            except Exception:
                print(traceback.format_exc())
                print(server, _items, type(server), type(_items))
                break


        server = self.col.find_one(search) # legacy backup

        _info = self.verify(search, serverList)

        if len(_info) > 0:
            info = random.choice(_info)
        else:
            info = server

        # for server in _info:
        #     # update the servers
        #     check(server["host"], port)

        return _info, info

    def genEmbed(self, _serverList, _port):
        """Generates an embed for the server list

        Args:
            serverList [list]: {
                "host":"ipv4 addr",
                "lastOnline":"unicode time",
                "lastOnlinePlayers": int,
                "lastOnlineVersion":"Name Version",
                "lastOnlineDescription":"Very Good Server",
                "lastOnlinePing":"unicode time",
                "lastOnlinePlayersList":["Notch","Jeb"],
                "lastOnlinePlayersMax": int,
                "favicon":"base64 encoded image"
            }

        Returns:
            [
                [interactions.Embed]: The embed,
                _file: favicon file,
                button: interaction button,
            ]
        """
        if len(_serverList) == 0:
            embed = interactions.Embed(
                title="No servers found",
                description="No servers found",
                color=0xFF0000,
            )
            buttons = [
                interactions.Button(
                    label='Show Players',
                    custom_id='show_players',
                    style=interactions.ButtonStyle.PRIMARY,
                    disabled=True,
                ),
                interactions.Button(
                    label='Next Server',
                    custom_id='rand_select',
                    style=interactions.ButtonStyle.PRIMARY,
                    disabled=True,
                ),
            ]

            row = interactions.ActionRow(components=buttons) # pyright: ignore [reportGeneralTypeIssues]

            return [embed, None, row]


        global ServerInfo
        random.shuffle(_serverList)
        info = _serverList[0]
        ServerInfo = info
        
        numServers = len(_serverList)
        online = True if self.check(info["host"], str(_port)) else False

        try:
            _serverList.pop(0)
        except IndexError:
            pass

        # setup the embed
        embed = interactions.Embed(
            title=("🟢 " if online else "🔴 ")+info["host"],
            description='```'+info["lastOnlineDescription"]+'```',
            color=(0x00FF00 if online else 0xFF0000),
            type="rich",
            fields=[
                interactions.EmbedField(name="Players", value=f"{info['lastOnlinePlayers']}/{info['lastOnlinePlayersMax']}", inline=True),
                interactions.EmbedField(name="Version", value=info["lastOnlineVersion"], inline=True),
                interactions.EmbedField(name="Ping", value=str(info["lastOnlinePing"]), inline=True),
                interactions.EmbedField(name="Cracked", value=f"{info['cracked']}", inline=True),
                interactions.EmbedField(name="Last Online", value=f"{(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(info['lastOnline']))) if info['host'] != 'Server not found.' else '0/0/0 0:0:0'}", inline=True),
            ],
            footer=interactions.EmbedFooter(text="Server ID: "+(str(self.col.find_one({"host":info["host"]})["_id"]) if info["host"] != "Server not found." else "-1")+'\n Out of {} servers'.format(numServers)) # pyright: ignore [reportOptionalSubscript]
        )


        try: # this adds the favicon in the most overcomplicated way possible
            if online: 
                stats = self.check(info["host"],str(_port)) 

                fav = stats["favicon"] if "favicon" in stats else None
                if fav is not None:
                    bits = fav.split(",")[1]

                    with open("server-icon.png", "wb") as f:
                        f.write(base64.b64decode(bits))
                    _file = interactions.File(filename="server-icon.png")
                    embed.set_thumbnail(url="attachment://server-icon.png")

                    print("Favicon added")
                else:
                    _file = None
            else:
                _file = None
        except Exception:
            print(traceback.format_exc(),info)
            _file = None

        players = self.check(info['host'])
        if players is not None:
            players = players['lastOnlinePlayersList'] if 'lastOnlinePlayersList' in players else []
        else:
            players = []

        buttons = [
            interactions.Button(
                label='Show Players',
                custom_id='show_players',
                style=interactions.ButtonStyle.PRIMARY,
                disabled=(len(players) == 0),
            ),
            interactions.Button(
                label='Next Server',
                custom_id='rand_select',
                style=interactions.ButtonStyle.PRIMARY,
                disabled=(len(_serverList) == 0),
            ),
        ]

        row = interactions.ActionRow(components=buttons) # pyright: ignore [reportGeneralTypeIssues]

        return embed, _file, row


    def cFilter(self, text):
        """Removes all color bits from a string

        Args:
            text [str]: The string to remove color bits from

        Returns:
            [str]: The string without color bits
        """
        # remove all color bits
        text = re.sub(r'§[0-9a-fk-or]', '', text).replace('|','')
        return text
        

    def crack(self, host, port="25565", username="pilot1782"):
        args = [host, '-p', port, '--offline-name', username]
        timeStart = time.time()
        try:
            chat.main(args)
        except twisted.internet.error.ReactorNotRestartable: # pyright: ignore [reportGeneralTypeIssues]
            pass
        except quarry.net.protocol.ProtocolError:
            return False
        except builtins.ValueError:
            return False
        except builtins.KeyError:
            pass
        except Exception:
            return False

        
        while True:
            if chat.flag:
                return True
            elif time.time() - timeStart > 10:
                return False
