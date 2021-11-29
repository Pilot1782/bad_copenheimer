from requests import get
import discord
from dotenv import load_dotenv
from discord.ext import commands
import time
from time import sleep
from mcstatus import MinecraftServer
import os
import subprocess


##################################################
#Stuff for you to change
TOKEN = 'YOUR TOKEN HERE' #Your discord bot token
lower_ip_bound = "10.0.0.0" # Lowest is 10.0.0.0
upper_ip_bound = "199.255.255.255" # Highest is 199.255.255.255
threads = 1020 # Max usable is 1000
timeout = 1000 # Ping timeout in miliseconds
path = r"qubo.jar" #Path to qubo.jar
os = 1 # What operating system you are using,0-Linux, 1-Windows
mascan = False # Do you have Masscan installed?
time2 = 1000000 #Max time allowed inbetween succsessful pings
##################################################




#################################################
# You don't need to change anything below this. #
#################################################


client = discord.Client()
bot = commands.Bot(command_prefix='!',help_command=None)
testing_b = False

def ptime():
  x = 0
  arr = []
  for i in time.localtime():
    x = x + 1
    if x == 2:
      print(f"Month {i}")
      arr.append(f"{i}/")
    if x == 3:
      print(f"Day {i}")
      arr.append(f"{i} ")
    if x == 1:
      print(f"Year {i}")
      arr.append(f"{i}/")
    if x == 4:
      if x > 12:
        x = x - 12
      print(f"Hour {i}")
      arr.append(f"{i}:")
    if x == 5:
      print(f"Min {i}")
      arr.append(f"{i}")
  out1 = ""
  for i in arr:
    out1 = out1 + i
  
  return out1

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


def testing():
  if testing_b:
    print(find(''))

@bot.command()
async def on_ready(self):
  print('Logged on as {0}!'.format(self.user))

@bot.command(name='mc')
async def _mc(ctx,*arg):
  await ctx.send(f"Scanning started: {ptime()}")
  arr = []

  ptime()
  print(f"Scanning {'172.65.238.0'}-{'172.65.240.255'} outputting {False}")
  arr = []
  if os == 0 and mascan == True:
    command = f"masscan -p25565 '172.65.238.0'-'172.65.240.255' --rate={threads * 3}".split()
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

  server = ''.join(arr)
  if server != None:
    await ctx.send(f"Testing the tool:\n{server}")

  await ctx.send(f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds.")
      
  print(f"\nPing on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")

  arr = []
  if os == 0 and mascan == True:
    command = f"masscan -p25565 {lower_ip_bound}-{upper_ip_bound} --rate={threads * 3}".split()
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
  elif os == 1:
    command = f"java -Dfile.encoding=UTF-8 -jar {path} -range {lower_ip_bound}-{upper_ip_bound} -ports 25565-25577 -th {threads} -ti {timeout}".split()
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
  await ctx.send(f"\nScanning finished at {ptime()}")
    
@bot.command(name='status')
async def _status(ctx,*args):
  msg = args

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

@bot.command(name='find')
async def _find(ctx,arg):
  msg = 'A Thing'#find(arg)
  try:
    if msg == None:
      await ctx.send("No output found.")
    else:
      await ctx.send(msg)
      print(msg)
  except:
    await ctx.send("Failed to find output.")

@bot.command(name='help')
async def _help(ctx):
  await ctx.send("Usage of all commands.\n\n!mc scans the range of ip specified in the dis-bot.pyw file.\n\n!status gets the status of the specified server.\nUsage:!status 10.0.0.0:25565\n\n!find scans all know servers in the outputs folder and returns if the given player is found.\nUsage:!find player123\n!cscan makes a custom scan\nUsage:\n!cscann 172.65.230.0 172.65.255.255")
  print("Printed Help")

@bot.command(name='cscan')
async def _cscan(ctx,arg1,arg2):
  await ctx.send(f"Scanning started: {ptime()}")
  arr = []

  ptime()
  print(f"Scanning {arg1}-{arg2} outputting {False}")
  arr = []
  if os == 0 and mascan == True:
    command = f"masscan -p25565 {arg1}-{arg2} --rate={threads * 3}".split()
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

if __name__ == "__main__":
  testing()
  bot.run(TOKEN)
