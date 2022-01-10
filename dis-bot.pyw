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
from javascript import require, On, Once, console


######################################################
#To change the settings, edit the settings.json file.#
######################################################



client = discord.Client()
bot = commands.Bot(command_prefix='!',help_command=None)
testing = False

if subprocess.check_output("whoami").decode("utf-8") != 'root\n' and os == 0:
  raise PermissionError(f"Please run as root, not as {subprocess.check_output('whoami').decode('utf-8')}")

with open(r"settings.json", "r") as read_file:
    data = json.load(read_file)
output_path = r"outputs.json"

mineflayer = require('mineflayer')
name = data["name"]
TOKEN = data["token"]
lower_ip_bound = data["lower_ip_bound"]
upper_ip_bound = data["upper_ip_bound"]
threads = data["threads"]
threads = int(threads)
timeout = data["timeout"]
timeout = int(timeout)
path = data["path"]
os = data["os"]
os = int(os)
mascan = data["mascan"]
mascan = bool(mascan)
time2 = data["time2"]

def write_json(new_data, filename='data.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["emp_details"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def ptime():
  x = 0
  arr = []
  tim = time.localtime()

  if tim.tm_hour > 12:
    arr.append(str(tim.tm_hour - 12))
  else:
    arr.append(str(tim.tm_hour))
  if tim.tm_min < 10:
    arr.append("0" + str(tim.tm_min))
  else:
    arr.append(str(tim.tm_min))
  
  return ':'.join(arr)

def MC(low,high,outb,threads1,time):
  ptime()
  print(f"Scanning {low}-{high} outputting {outb}")
  arr = []
  if os == 0 and mascan == True:
    command = f"masscan -p25565 {low}-{high} --rate={threads1 * 3}".split()
    for line in run_command(command):
      print(line.decode("utf-8"))
      arr.append(line.decode("utf-8"))
  elif os == 1:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -range {low}-{high} -ports 25565-25577 -th {threads1} -ti {time}".split()
    for line in run_command(command):
      print(line.decode("utf-8"))
      arr.append(line.decode("utf-8"))
  return ''.join(arr)

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

def file_out():
  try:
    if os == 0:
      outpt = subprocess.check_output("ls outputs",shell=True)
    elif os == 1:
      outpt = subprocess.check_output("dir",shell=True)
    outpt = outpt.decode("utf-8")
    outpt = outpt.split('\n')
    return outpt
  except:
    return "No Output folder made."  

def find(player):
  files = file_out()
  outp = []
  msg = []
  
  if files == "No Output folder made.":
    return "No Output folder made."
  else:
    try:
      for i in files:
        server = MinecraftServer.lookup("example.org:1234")

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



def server_join(ip):
  pass


def testing():
  pass

@bot.command()
async def on_ready(self):
  print('Logged on as {0}!'.format(self.user))

@bot.command(name='mc')
async def _mc(ctx):
  await ctx.send(f"Scanning started: {ptime()}")
  arr = []

  ptime()
  await ctx.send("Testing the Tool")
  print(f"Scanning {'172.65.238.0'}-{'172.65.240.255'} outputting False")
  arr = []
  if os == 0 and mascan == True:
    print("scanning using masscan")
    command = f"sudo masscan 172.65.238.0-172.65.240.255 -p25565 --rate=100000 --exclude 255.255.255.255"
    for line in run_command(command):
      line = line.decode("utf-8")
      try:
        if "rate" in line:
          print("Skipped")
        else:
          print(line)
          await ctx.send(line)
      except:
        await ctx.send(".")
  elif os == 1:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -range 172.65.238.0-172.65.240.255 -ports 25565-25577 -th {threads} -ti {timeout}".split()
    for line in run_command(command):
      line = line.decode("utf-8")
      print(line)
      if line == '' or line == None:
        pass
      else:
        try:
          await ctx.send(line)
        except:
          await ctx.send(".")


  await ctx.send(f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds.")
      
  print(f"\nScanning on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")

  


  if os == 0 and mascan == True:
    print("scanning using masscan")
    command = f"sudo masscan {lower_ip_bound}-{upper_ip_bound} -p25565 --rate={threads * 3} --exclude 255.255.255.255 -oj outputs.json"
    for line in run_command(command):
      line = line.decode("utf-8")
      try:
        if "rate" in line:
          print("Skipped")
        else:
          print(line)
          await ctx.send(line)
      except:
        await ctx.send(".")
  elif os == 1:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -range {lower_ip_bound}-{upper_ip_bound} -ports 25565-25577 -th {threads} -ti {timeout}".split()
    arr= []
    for line in run_command(command):
      line = line.decode("utf-8")
      print(line)
      if line == '' or line == None:
        pass
      else:
        try:
          await ctx.send(line)
          arr.append(line)
        except:
          await ctx.send(".")
    a = []
    for i in arr:
      if i.startswith("(1"):
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
  await ctx.send(f"\nScanning finished at {ptime()}")
  with open(output_path) as fp:
    data = json.load(fp)
    
    for i in b:
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
        server = MinecraftServer.lookup(i)
        status = server.status()
        mesg = "The server has {0} players and replied in {1} ms\n".format(status.players.online, status.latency)
        print(mesg)
        await ctx.send(mesg)
      except:
        await ctx.send(f"Failed to scan {i}.\n")
        print(f"Failed to scan {i}.\n")
        
      try: #Try quering server
        server = MinecraftServer.lookup(i)
        query = server.query()
        print("The server has the following players online: {0}".format(", ".join(query.players.names)))
        await ctx.send("The server has the following players online: {0}".format(", ".join(query.players.names)))
      except:
        print(f"Failed to query {i}")
        await ctx.send(f"Failed to query {i}.")
  else:

    with open(r'D:\Carson\Programming\Python_Stuff\bad_copeheimer-main\bad_copeheimer-main\outputs.json') as json_file:
      data = json.load(json_file)
      await ctx.send("Scanning {0} servers".format(len(data)))
      c = 0
      u = 0
      lst = data
      er = []
      for p in lst:
        #find the status of p
        p = p["ip"]
        try:  #Try getting the status and catch the errors
          try: #Nested try to get the status
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

@bot.command(name='find')
async def _find(ctx,arg):
  msg = arg
  try:
    await("Finding {0}".format(msg))
  except:
    await ctx.send("No player specified.")

@bot.command(name='help')
async def _help(ctx):
  await ctx.send("Usage of all commands.\n\n!mc scans the range of ip specified in the dis-bot.pyw file.\n\n!status gets the status of the specified server.\nUsage:!status 10.0.0.0:25565\nTo test the connectivity of the servers in the output file.\n\n!find scans all know servers in the outputs folder and returns if the given player is found.\nUsage:!find player123\n!cscan makes a custom scan\nUsage:\n!cscann 172.65.230.0 172.65.255.255")
  print("Printed Help")

@bot.command(name='cscan')
async def _cscan(ctx,arg1,arg2):
  await ctx.send(f"Scanning started: {ptime()}")

  ptime()
  print(f"Scanning {arg1}-{arg2} outputting {False}")
  
  if os == 0 and mascan == True:
    print("scanning using masscan")
    command = f"sudo masscan {arg1}-{arg2} -p25565,25566,25567 --rate=100000 --exclude 255.255.255.255"
    for line in run_command(command):
      line = line.decode("utf-8")
      try:
        if "rate" in line:
          print("Skipped")
        else:
          print(line)
          await ctx.send(line)
      except:
        await ctx.send(".")
  elif os == 1:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -range {arg1}-{arg2} -ports 25565-25577 -th {threads} -ti {timeout}".split()
    for line in run_command(command):
      line = line.decode("utf-8")
      print(line)
      if line == '' or line == None:
        pass
      else:
        try:
          await ctx.send(line)
        except:
          await ctx.send(".")
  await ctx.send(f"\n\nScanning finished at {ptime()}")

if __name__ == "__main__":
  if not testing:
    bot.run(TOKEN)
  else:
    bot.run(TOKEN)
