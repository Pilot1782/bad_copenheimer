from requests import get
import discord
from dotenv import load_dotenv
from discord.ext import commands
import time
from time import sleep
from mcstatus import MinecraftServer
import os
import subprocess
import json
import multiprocessing



'''
To change the main settings, edit the settings.json file.
Below this is preconfigured
'''

settings_path = 'D:\\Carson\\Programming\\Python_Stuff\\bad_copeheimer-main\\bad_copeheimer-main\\bad_copenheimer\\settings.json'
# Varaible getting defeined
client = discord.Client()
bot = commands.Bot(command_prefix='!',help_command=None)

with open(settings_path, "r") as read_file: # Open the settings file and start defineing variables from it
  data = json.load(read_file)

testing = data["testing"] #bc it easier
home_dir = data["home-dir"]
output_path = home_dir + "outputs.json"
name = data["name"]
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
path = home_dir + "qubo.jar"
mascan = data["masscan"]
time2 = data["time2"]
debug = data["debugging"]
passwd = data["password"]
server = data["server"]
sport = data["server-port"]

# Check if you are root for running masscan
if subprocess.check_output("whoami").decode("utf-8") != 'root\n' and os == 0:
  raise PermissionError(f"Please run as root, not as {subprocess.check_output('whoami').decode('utf-8')}")

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
def run_command(command):
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
        sleep(.1) #Don't waste CPU-cycles
    # Empty STDERR buffer
    err = p.stderr.read()
    if p.returncode != 0:
       # The run_command() function is responsible for logging STDERR 
       print(str(err))
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

def dprint(text):
  if debug:
    print(text)

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
      if "Discovered" in i.decode("utf-8"):
        yield clean(i.decode("utf-8"))
    os.removedirs(f"{home_dir}outputs")

def halt():
  for line in run_command(f"{home_dir}stopper.pyw"):
    if "halt" in line:
      global flag
      flag = True

####################
# Discord commands #
####################

# On login to server
@bot.command()
async def on_ready(self):
  print('Logged on as {0}!'.format(self.user))

# Scan the large list
@bot.command(name='mc')
async def _mc(ctx):

  await ctx.send(f"Scanning started: {ptime()}")
  arr = []

  print(ptime())
  await ctx.send("Testing the Tool")
  print(f"Scanning {'172.65.238.0'}-{'172.65.240.255'}")
  arr = []
  if os == 0 and mascan == True:
    print("testing using masscan")

    for line in scan("172.65.238.0","172.65.239.0"):
      if flag == True:
        break
      try:
        if "D" in line:
          bol = True
          cnt += 1
          break
      except:
        bol = False
    if bol:
      print("Test passed!")
      await ctx.send("Test passed!\n{0} hosts found".format(cnt))
    else:
      print("Test failed.")
      await ctx.send("Test Failed.")
  else:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -nooutput -range 172.65.238.0-172.65.240.255 -ports 25565-25577 -th {threads} -ti {timeout}"
    bol = False
    dprint(command)
    for line in run_command(command):
      line = line.decode("utf-8")
      try:
        if "(" in line:
          bol = True
      except:
        bol = False
    if bol:
      print("Test passed!")
      await ctx.send("Test passed!")
    else:
      print("Test failed.")
      await ctx.send("Test Failed.")


  await ctx.send(f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds.")
      
  print(f"\nScanning on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")

  
  outp = []
  if os == 0 and mascan == True:
    command = f"sudo masscan -p25565 {lower_ip_bound}-{upper_ip_bound} --rate={threads * 3} --exclude 255.255.255.255"
    bol = False
    cnt = 0
    dprint(command)
    for line in run_command(command):
      line = line.decode("utf-8")
      line = clean(line)
      try:
        if "." in line:
          bol = True
          cnt += 1
          arr.append(line)
          print(line)
          await ctx.send(line)
      except:
        bol = False
    
    outp = arr
    dprint(outp)
    
  else:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -nooutput -range {lower_ip_bound}-{upper_ip_bound} -ports 25565-25577 -th {threads} -ti {timeout}"
    arr= []
    if debug:
      print(command)
    for line in run_command(command):
      line = line.decode("utf-8")
      print(line)
      if line == '' or line == None:
        pass
      else:
        try:
          if line.startswith("[") or line.startswith("("):
            await ctx.send(line)
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
    
    print("{0}\n{1}".format(b,len(b)))
    outp = b
  await ctx.send(f"\nScanning finished at {ptime()}")
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


    with open(filename, 'w') as json_file:
       json.dump(data, json_file, 
                            indent=4,  
                            separators=(',',': '))
 
    print('Successfully appended {0} lines to the JSON file'.format(len(data)))

  if proc.is_alive:
    proc.terminate()
  proc.join()
    
# Get the status of a specified server or all of the saved servers
@bot.command(name='status')
async def _status(ctx,*args):
  try:
    msg = args
  except:
    msg = ""

  if len(msg) > 0:
    print(f"Scan of {msg} requested.")
        
    for i in args:
      try: #Try getting the status
        from mcstatus import MinecraftServer
        server = MinecraftServer.lookup(i)
        status = server.status()
        mesg = "The server has {0} players and replied in {1} ms\n".format(status.players.online, status.latency)
        print(mesg)
        await ctx.send(mesg)
      except Exception as err:
        await ctx.send(f"Failed to scan {i}.\n")
        print("Failed to scan {0}.\n{1}".format(i,err))
        
      try: #Try quering server
        from mcstatus import MinecraftServer
        server = MinecraftServer.lookup(i)
        query = server.query()
        print("The server has the following players online: {0}".format(", ".join(query.players.names)))
        await ctx.send("The server has the following players online: {0}".format(", ".join(query.players.names)))
      except:
        print(f"Failed to query {i}")
        await ctx.send(f"Failed to query {i}.")
  else:
    with open(output_path) as json_file:
      data = json.load(json_file)
      await ctx.send("Scanning {0} servers".format(len(data)))
      c = 0
      u = 0
      lst = data
      er = []
      for p in lst:
        #find the status of ips
        p = p["ip"]
        try:  #Try getting the status and catch the errors
          try: #Nested trying bc otherwise if i make a mistake then it fails but i alread fixed it but i don't want to remove the nested trying bc im too lazy but I'll do it next commit, I promise
            from mcstatus import MinecraftServer
            server = MinecraftServer.lookup(p)
            status = server.status()
            mesg = "{0} has {1} players and replied in {2} ms\n".format(p, status.players.online, status.latency)
            print(mesg)
            await ctx.send(mesg)
            c += 1
            u += 1
          except Exception as e: #Catch the error
            if not str(e) in er:
              er.append(str(e))
            print("Failed to scan {0} due to {1} \n {2}:{3}".format(p, e, c, u))
            c += 1
        except Exception as err: #Catches all other errors
          if not str(err) in er:
            er.append(str(err))
          print("Failed to scan {0} due to {1} \n {2}:{3}".format(p, err, c, u))
          c += 1
      er = list(set(er)) #Remove duplicates
      er = "\n".join(er)
      await ctx.send("Scanning finished.\n{1} out of {0} are up.\nThe following Errors occured:\n{2}".format(len(data), u, er))
      print("Scanning finished.\n{1} out of {0} are up.\nThe following Errors occured:\n{2}".format(len(data), u, er))

# Find a player currently playing on a server
@bot.command(name='find')
async def _find(ctx,arg):
  msg = arg
  try:
    await("Finding {0}".format(msg))
  except:
    await ctx.send("No player specified.")

# List all of the commands and how to use them
@bot.command(name='help')
async def _help(ctx):
  await ctx.send("Usage of all commands.\n\n!mc scans the range of ip specified in the dis-bot.pyw file.\n\n!status gets the status of the specified server.\nUsage:!status 10.0.0.0:25565\nTo test the connectivity of the servers in the output file.\n\n!find scans all know servers in the outputs folder and returns if the given player is found.\nUsage:!find player123\n!cscan makes a custom scan\nUsage:\n!cscann 172.65.230.0 172.65.255.255")
  print("Printed Help")

# Print whether debugging and testing are active
if __name__ == "__main__":
  print("Testing:{0}, Debugging:{1}\n".format(testing,debug))
  try:
    if testing:
      proc = multiprocessing.Process(target=run_command, args=("python3 stopper.pyw",))
      proc.start()
      bot.run(TOKEN)
      proc.join()
    else:
      proc = multiprocessing.Process(target=run_command, args=("python3 stopper.pyw",))
      proc.start()
      bot.run(TOKEN)
      proc.join()
  except Exception as err:
    if debug:
      print("\n{0}".format(err))
    print("\nSorry, Execution of this file has failed.")


















































    # Now its 500 lines