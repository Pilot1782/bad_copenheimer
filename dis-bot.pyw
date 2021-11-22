from requests import get
import discord
from dotenv import load_dotenv
from discord.ext import commands
import time
from mcstatus import MinecraftServer
import os
import subprocess


##################################################
#Stuff for you to change
TOKEN = 'YOUR TOKEN HERE' #Your discord bot token
lower_ip_bound = "10.0.0.0" #Lowest is 10.0.0.0
upper_ip_bound = "199.255.255.255" #Highest is 199.255.255.255
threads = 255 #Max usable is 1000
timeout = 1000 #Ping timeout in miliseconds
path = r"qubo.jar" #Path to qubo.jar
os = 1 #What operating system you are using,0-Linux, 1-Windows
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
      print(f"Hour {i}")
      arr.append(f"{i}:")
    if x == 5:
      print(f"Min {i}")
      arr.append(f"{i}")
  out1 = ""
  for i in arr:
    out1 = out1 + i
  
  return out1

def MC(range,outb,threads,time):
  import subprocess
  ptime()
  print(f"Scanning {range} outputting {outb}")
  try:
    outp = subprocess.check_output(f"java -Dfile.encoding=UTF-8 -jar {path} -range {range} -ports 25565-25577 -th {threads} -ti {time}",shell=True)
  except:
    print("Sorry, execution failed.")
    return "Sorry, execution failed."
  if outb == True:
    print(outp.decode("utf-8"))
  outp = outp.decode("utf-8")

  #reomove the first 5 letters of outp
  outp = outp[400:]

  return outp

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
    return '\n'.join(outp)


def testing():
  if testing_b:
    print(find(''))

@bot.command()
async def on_ready(self):
  print('Logged on as {0}!'.format(self.user))

@bot.command(name='mc')
async def _mc(ctx,*arg):
  await ctx.send(f"Scanning started: {ptime()}")
      
  server = MC("172.65.238.*",False,255,timeout)
  print(server)

  await ctx.send(f"Testing the tool:\n{server}")

  await ctx.send(f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds.")
      
  print(f"\nPing on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")
      
  scan = MC(f"{lower_ip_bound}-{upper_ip_bound}",True,threads,timeout)

  await ctx.send(f"\nIt's Finally Done!\n\n{scan}")
    
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
  msg = find(arg)
  if msg == None:
    await ctx.send("No output found.")
  else:
    await ctx.send(msg)
    print(msg)

@bot.command(name='help')
async def _help(ctx):
  await ctx.send("Usage of all commands.\n\n!mc scans the range of ip specified in the dis-bot.pyw file.\n\n!status gets the status of the specified server.\nUsage:!status-10.0.0.0:25565\n\n!find scans all know servers in the outputs folder and returns if the given player is found.\nUsage:!find player123")
  print("Printed Help")


if __name__ == "__main__":
  testing()
  bot.run(TOKEN)
