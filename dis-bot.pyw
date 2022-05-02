from turtle import home
from requests import get
import discord
from discord.ext import commands
import time
from time import sleep
from mcstatus import MinecraftServer
import os as osys
import subprocess
import json
import multiprocessing
from funcs import *


##############################################################
#To change the main settings, edit the settings.json file.#
##############################################################

settings_path = osys.getenv("PATH")
###############################
# Below this is preconfigured #
###############################

# Check if you are root for running masscan
if os == 0 and subprocess.check_output("whoami",shell=True).decode("utf-8") != 'root\n':
  raise PermissionError(f"Please run as root, not as {subprocess.check_output('whoami').decode('utf-8')}")

settings_path = osys.getenv("PATH")
# Varaible getting defeined
client = discord.Client()
bot = commands.Bot(command_prefix='!',help_command=None)

with open(settings_path, "r") as read_file: # Open the settings file and start defineing variables from it
  data = json.load(read_file)

testing = data["testing"] #bc it easier
home_dir = data["home-dir"]
output_path = home_dir + "outputs.json"
usr_name = data["user"]
if not testing:
  TOKEN = data["TOKEN"]
else:
  TOKEN = osys.getenv("TOKEN")
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

# Check if you are root for linux
try:
  if os == 0:
    if subprocess.check_output("whoami", shell=True).decode("utf-8") != 'root\n':
      raise PermissionError(f"Please run as root, not as {subprocess.check_output('whoami', shell=True).decode('utf-8')}")
except Exception as e:
  if e == PermissionError:
    print(f"Please run as root, not as {subprocess.check_output('whoami',shell=True).decode('utf-8')}")
    log(e)
    exit()



####################
# Discord commands #
####################

# Scan the large list
@bot.command(name='mc')
async def _mc(ctx, args):
  log("Command: mc run" + str(args))
  # Start a process that runs stoper.pyw
  def stopper():
    if testing:
      os.system("python3 {0}stoper.pyw --test".format(home_dir))
    else:
      os.system("python3 {0}stoper.pyw".format(home_dir))
  
  proc = multiprocessing.Process(target=stopper)
  proc.start()


  await ctx.send(f"Scanning started: {ptime()}")
  arr = []

  print(ptime())
  await ctx.send("Testing the Tool")
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
      print("Test passed!")
      await ctx.send("Test passed!\n{0} hosts found".format(cnt))
    else:
      print("Test failed.")
      await ctx.send("Test Failed.")
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
      print("Test passed!")
      await ctx.send("Test passed!")
    else:
      print("Test failed.")
      await ctx.send("Test Failed.")

  if len(args) > 0:
    lower_ip_bound = args[0]
    upper_ip_bound = args[1]
  
    testar = args[0].split(".")
    if len(testar) != 4:
      await ctx.send("Invalid IP")
      exit()
    testar = args[1].split(".")
    if len(testar) != 4:
      await ctx.send("Invalid IP")
      exit()

  await ctx.send(f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds.")
      
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
    for line in scan(lower_ip_bound, upper_ip_bound):
      if flag:
        break
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
    
    dprint("{0}\n{1}".format(b,len(b)))
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

    dprint(outp)

    with open(filename, 'w') as json_file:
       json.dump(data, json_file, 
                            indent=4,  
                            separators=(',',': '))
    dprint(data)
    print('Successfully appended {0} lines to the JSON file'.format(len(data)))
    await ctx.send('Successfully appended {0} lines to the JSON file'.format(len(data)))
    log("Successfully appended {0} lines to the JSON file".format(len(data)))

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
    log(f"Scan of {msg} requested.")
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
        log(err)
        
      try: #Try quering server
        from mcstatus import MinecraftServer
        server = MinecraftServer.lookup(i)
        query = server.query()
        print("The server has the following players online: {0}".format(", ".join(query.players.names)))
        await ctx.send("The server has the following players online: {0}".format(", ".join(query.players.names)))
      except Exception as err:
        print(f"Failed to query {i}")
        await ctx.send(f"Failed to query {i}.")
        log(err)
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
            log(e)
        except Exception as err: #Catches all other errors
          if not str(err) in er:
            er.append(str(err))
          print("Failed to scan {0} due to {1} \n {2}:{3}".format(p, err, c, u))
          c += 1
          log(err)
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
  await ctx.send("""Usage of all commands.
  
!mc | scans the range of ip specified in the dis-bot.pyw file.
Usage: !mc [ip range]

!status | gets the status of the specified server.
Usage:!status 10.0.0.0:25565

To test the connectivity of the servers in the output file.
Usage:!status

!find | scans all know servers in the outputs folder and returns if the given player is found. (Very WIP)
Usage:!find player123

Custom scans, scan a custom set of ips.
Usage: !mc 10.0.0. 10.0.0.255

!stop | usable when ran with !mc, stops the scan from completing
Usage: !stop

!kill | Last Resort Only!, Kills all python procs.
Usage: !kill""")
  print("Printed Help")

#Startup
def startup():
  bot.run(TOKEN)

# Print whether debugging and testing are active
if __name__ == "__main__":
  print("Testing:{0}, Debugging:{1}\n".format(testing,debug))
  try:
    if testing:
      flag = True
      proc2 = multiprocessing.Process(target=startup,args=())
      proc2.start()
      if os == 1:
        pypath = r"%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
      else:
        pypath = "python3"
      for line in run_command(r"{} stopper.pyw".format(pypath)):
        print(line.decode("utf-8"))
        if line.decode("utf-8") == "BAIL|A*(&HDO#QDH" and proc2.is_alive():
          proc2.terminate()
          print("Stopped")
          break

      proc2.join()
    else:
      proc = multiprocessing.Process(target=run_command, args=("python3 stopper.pyw",))
      proc.start()
      bot.run(TOKEN)
      proc.join()
  except Exception as err:
    print("\n\nSorry, Execution of this file has failed, see the log for more details.\n")
    log(err)