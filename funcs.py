import subprocess
import json
import time
import os as osys
from mcstatus import JavaServer


class funcs:
    """_summary_
            # STOP HERE

            Beyond this point is code unmaintained and at risk of mabye being important.
            Once this file was made, no proper docs on the methods have been made except those that I sometimes remember.

    """    

    def __init__(self):
        self.path = osys.path.dirname(osys.path.abspath(__file__))

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
        self.home_dir = data["home-dir"]
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
        self.path = self.home_dir + "qubo.jar"
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
        """_summary_

        Args:
            command (raw string): desired command
            powershell (bool, optional): use powershell for windows. Defaults to False.

        Returns:
            string: error message

        Yields:
            string: console output of command
        """

        if powershell:
            command = rf"C:\Windows\system32\WindowsPowerShell\\v1.0\powershell.exe -command {command}"
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        # Read stdout from subprocess until the buffer is empty !
        for line in iter(p.stdout.readline, b""):
            if line:  # Don't print blank lines
                yield line
        # This ensures the process has completed, AND sets the 'returncode' attr
        while p.poll() is None:
            time.sleep(0.1)  # Don't waste CPU-cycles
        # Empty STDERR buffer
        err = p.stderr.read()
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
        """_summary_

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
    def dprint(self, text):
        if self.debug:
            print(text)

    # Scan to increase simplicity
    def scan(self, ipL, ipU): # dont use scan_range
        """_summary_

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
    def log(self, text):
        with open(f"{self.home_dir}log.txt", "a") as f:
            f.write(f"[{self.ptime()}] {text}\n")

    # Scan a range
    def scan_range(self, ip1, ip2): #legacy verson of scan
        """_summary_

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
