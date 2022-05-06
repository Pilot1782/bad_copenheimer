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
  with open(f"{path}log.txt", "a") as f:
    f.write(f"[{ptime()}] {text}\n")

#Scan a range
def scan_range(ip1, ip2):
  yield f"Scanning started: {ptime()}"

  flag = False
  print(ptime())
  yield "Testing the Tool"
  print(f"Scanning {'172.65.238.0'}-{'172.65.240.255'}")
  arr = []
  if os == 0 and mascan == True:
    print("testing using masscan")

    for line in scan("172.65.238.0","172.65.239.0"):
      if flag:
        break
      try:
        dprint(line)
        if "D" in line:
          bol = True
          break
      except:
        bol = False
    if bol:
      dprint("Test passed!")
      yield "Test passed!"
    else:
      dprint("Test failed.")
      log("Test failed.")
      yield "Test Failed."
  else:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -nooutput -range 172.65.238.0-172.65.240.255 -ports 25565-25577 -th {threads} -ti {timeout}"
    bol = False
    dprint(command)
    for line in list(scan('172.65.238.0','172.65.240.255')):
      if flag:
        break
      if "(" in line:
        bol = True
        break
    if bol:
      dprint("Test passed!")
      yield "Test passed!"
    else:
      dprint("Test failed.")
      yield "Test Failed."
  
  yield f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds."
      
  print(f"\nScanning on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")

  
  outp = []
  if os == 0 and mascan == True:
    command = f"sudo masscan -p25565 {lower_ip_bound}-{upper_ip_bound} --rate={threads * 3} --exclude 255.255.255.255"
    bol = False
    cnt = 0
    dprint(command)
    for line in scan(lower_ip_bound, upper_ip_bound):
      if flag:
        break
      try:
        if "." in line:
          bol = True
          cnt += 1
          arr.append(line)
          print(line)
          yield line
      except:
        bol = False
    
    outp = arr
    dprint(outp)
    
  else:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -nooutput -range {lower_ip_bound}-{upper_ip_bound} -ports 25565-25577 -th {threads} -ti {timeout}"
    arr= []
    if debug:
      print(command)
    for line in scan(lower_ip_bound, upper_ip_bound):
      if flag:
        break
      if line == '' or line == None:
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
        else:
          if j == "(":
            pass
          else:
            f.append(j)
      b.append("".join(f))
    
    dprint("{0}\n{1}".format(b,len(b)))
    outp = b

  yield f"\nScanning finished at {ptime()}"
  with open(output_path) as fp:
    data = json.load(fp)
    for i in outp:
      bol = False
      for j in data:
        if i in j['ip']:
          bol = False
          break
        else:
          bol = True
      if bol:
        data.append({"ip": i,"timestamp": "1641565033","ports": [{"port": 25565,"proto": "tcp","status": "open","reason": "syn-ack","ttl": 64}]})
    filename = output_path

    dprint(outp)

    with open(filename, 'w') as json_file:
       json.dump(data, json_file, 
                            indent=4,  
                            separators=(',',': '))
    dprint(data)
    print('Successfully appended {0} lines to the JSON file'.format(len(data)))
    yield 'Successfully appended {0} lines to the JSON file'.format(len(data))
    log("Successfully appended {0} lines to the JSON file".format(len(data)))