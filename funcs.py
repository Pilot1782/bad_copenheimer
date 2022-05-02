import subprocess
import json
import time
import os
from mcstatus import MinecraftServer

settings_path = os.getenv("PATH")

with open(settings_path, "r") as read_file: # Open the settings file and start defineing variables from it
  data = json.load(read_file)

testing = data["testing"] #bc it easier
home_dir = data["home-dir"]
output_path = home_dir + "outputs.json"
usr_name = data["user"]
if not testing:
  TOKEN = data["TOKEN"]
else:
  TOKEN = os.getenv("TOKEN")
lower_ip_bound = data["lower_ip_bound"]
upper_ip_bound = data["upper_ip_bound"]
threads = data["threads"]
threads = int(threads)
timeout = data["timeout"]
timeout = int(timeout)
os = data["os"]
os = int(os)
if os == 1:
  osp = "\\"
else:
  osp = "/"
path = home_dir + "qubo.jar"
mascan = data["masscan"]
time2 = data["time2"]
debug = data["debugging"]
passwd = data["password"]
server = data["server"]
sport = data["server-port"]


# Functions getting defeined

# Write to a json file
def write_json(new_data, filename='data.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["emp_details"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

# Print the Time
def ptime():
  x = time.localtime()
  z = []
  for i in x:
    z.append(str(i))
  y = ":".join(z)
  z = f"{z[0]} {z[1]}/{z[2]} {z[3]}:{z[4]}:{z[5]}"
  return z

# Start a python server
def hserver():
  if server:
    os.system("python -m http.server {0}".format(sport))

# Run a command and get line by line output
def run_command(command,powershell=False):
    if powershell:
      command = f"C:\Windows\system32\WindowsPowerShell\\v1.0\powershell.exe -command {command}"
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    # Read stdout from subprocess until the buffer is empty !
    for line in iter(p.stdout.readline, b''):
      if line: # Don't print blank lines
          yield line
    # This ensures the process has completed, AND sets the 'returncode' attr
    while p.poll() is None:
        time.sleep(.1) #Don't waste CPU-cycles
    # Empty STDERR buffer
    err = p.stderr.read()
    if p.returncode != 0:
       # The run_command() function is responsible for logging STDERR 
       print(str(err))
       log(str(err))
       return ("Error: " + str(err))

# Login into a minecraft server
flag = False
def login(host):
  global usr_name, passwd, home_dir, flag
  for i in run_command("python3 {4}playerlist.pyw --auth {0}:{1} -p {2} {3}".format(usr_name,passwd,25565,host,home_dir)):
    dprint(i.decode("utf-8"))
    return i.decode("utf-8")
    flag = True

# Get the file output depending on the os
def file_out():
  with open(output_path, "r") as f:
    data1 = json.load(f)
    for i in data1:
      return i["ip"]

# Look through your files and see if the server you scan has 'player' playing on it, going to be redon soon
# The redoo may be implemented but i have to test the file first.
def find(player):
  outp = []
  with open(f"{home_dir}outputs.json", "r") as f:
    data = json.load(f)
    try:
      for i in data:
        ip = i["ip"]
        server = MinecraftServer.lookup(f"{ip}:25565")

        status = server.status()
        print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))

        # 'ping' is supported by all Minecraft servers that are version 1.7 or higher.
        # It is included in a 'status' call, but is exposed separate if you do not require the additional info.
        latency = server.ping()
        print("The server replied in {0} ms".format(latency))

        # 'query' has to be enabled in a servers' server.properties file.
        # It may give more information than a ping, such as a full player list or mod information.
        query = server.query()
        print("The server has the following players online: {0}".format(", ".join(query.players.names)))
    except:
      outp.append("Sorry, execution failed.")

    print('\n'.join(outp))
    return 'Done\n'.join(outp)

#Clean masscan output
def clean(line):
    if "rate" in line:
      print("Skipped")
    else:
        arr = []
        words = ["Discovered","open","port","25565/tcp","on"]
        line = line.split(" ")
        for i in line:
          if i in words:
            pass
          else:
            arr.append(i)
        return "".join(arr)

#Print but for debugging
def dprint(text):
  if debug:
    print(text)

#Scan to increase simplicity
def scan(ip1, ip2):
  global mascan, home_dir, path, timeout, threads, os
  if os == 0 and mascan == True:
    command = f"sudo masscan -p25565 {ip1}-{ip2} --rate={threads * 3} --exclude 255.255.255.255"
    for i in run_command(command):
      dprint(i.decode("utf-8"))
      if "Discovered" in i.decode("utf-8"):
        yield clean(i.decode("utf-8"))
  else:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -range {ip1}-{ip2} -ports 25565-25577 -th {threads} -ti {timeout}"
    for i in run_command(command):
      dprint(i.decode("utf-8"))
      if "(" in i.decode("utf-8"):
        yield clean(i.decode("utf-8"))
    import os as osys
    osys.chdir("outputs")
    files = osys.listdir(osys.getcwd())
    for i in files:
      if i.endswith(".txt"):
        osys.remove(f"{home_dir}outputs\\{i}")

#Stop command
def halt():
  for line in run_command(f"{home_dir}stopper.pyw"):
    if "halt" in line:
      global flag
      flag = True

#If error then log it
def log(text, path=home_dir):
  print("[Error]"+text)
  with open(f"{path}log.txt", "a") as f:
    f.write(f"[{ptime()}] {text}\n")