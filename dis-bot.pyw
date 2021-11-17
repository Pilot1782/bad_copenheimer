from requests import get
import discord
from dotenv import load_dotenv
from discord.ext import commands
import time
from mcstatus import MinecraftServer
import os
from os import listdir
import subprocess


##################################################
#Stuff for you to change
TOKEN = 'YOUR TOKEN HERE' #Your discord bot token
lower_ip_bound = "10.0.0.0" #Lowest is 10.0.0.0
upper_ip_bound = "199.255.255.255" #Highest is 199.255.255.255
threads = 255 #Max usable is 1000
timeout = 1000 #Ping timeout in miliseconds
path = r"qubo.jar" #Path to qubo.jar
os = 0 #What operating system you are using,0-Linux, 1-Windows
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
    print(outp)
  return outp

def file_out():
  if os == 0:
    outpt = subprocess.check_output("ls outputs",shell=True)
  elif os == 1:
    for name in os.listdir("."):
      if name.endswith(".txt"):
          outp.append(name)
  outpt = outpt.decode("utf-8")
  outpt = outpt.split('\n')
  return outpt
  

def find(player):
  files = file_out()
  outp = []
  msg = []
  for i in files:
    if i == '':
      pass
    else:
      path = "outputs/" + i
      with open(path) as f:
        lines = f.readlines()
        outp.append(lines)
  for i in outp:
    for j in i:
      if '(' in j:
        c = 0
        ip_addr = []
        for k in j:
          if k == ')':
            break
          else:
            ip_addr.append(k)
        ip_addr = ''.join(ip_addr)
        ip_addr = ip_addr.replace('(','',1)
        msg.append(ip_addr)
  
  outp = []
  for i in msg:
    server = i
    try:
      query = server.query()
      if player in query.players.names:
        msg = f"Found {player} on {i}"
      if msg == "":
        pass
      else:
        return msg
        print(msg)
    except:
      outp.append(f"quering isn't supported on {i}")
    
  return '\n'.join(outp)
  print('\n'.join(outp))

def testing():
  if testing_b:
    print(find(''))

async def on_ready(self):
  print('Logged on as {0}!'.format(self.user))

@bot.command(name='mc')
async def _mc(ctx,*arg):
  await ctx.send(f"Scanning started: {ptime()}")
      
  server = MC("172.65.238.*",False,255,timeout)
  server = server.decode("utf-8")
  print(server)

  await ctx.send(f"Testing the tool:\n{server}")

  await ctx.send(f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds.")
      
  print(f"\nPing on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")
      
  scan = MC(f"{lower_ip_bound}-{upper_ip_bound}",True,threads,timeout)

  scan = scan.decode("utf-8")

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
  msg = message.content
  for i in "find!-":
    msg.replace(i,"",1)
  await ctx.send(find(msg))

@bot.command(name='help')
async def _help(ctx):
  await ctx.send("Usage of all commands.\n\nmc! scans the range of ip specified in the dis-bot.pyw file.\n\nstatus! gets the status of the specified server.\nUsage:status!-10.0.0.0:25565\n\nfind! scans all know servers in the outputs folder and returns if the given player is found.\nUsage:find!-player123")


if __name__ == "__main__":
  testing()
  print("Starting")
  client.run(TOKEN)