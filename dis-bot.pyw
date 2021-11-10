from requests import get
import discord
from dotenv import load_dotenv
from discord.ext import commands
import time
from mcstatus import MinecraftServer
import os


##################################################
#Stuff for you to changeTOKEN = 'YOUR TOKEN HEREE' #Your discord bot token
lower_ip_bound = "172.0.0.0" #Lowest is 10.0.0.0
upper_ip_bound = "192.255.255.255" #Highest is 199.255.255.255
threads = 255 #Max usable is 1000
timeout = 1000 #Ping timeout in miliseconds
path = r"qubo.jar" #Path to qubo.jar
##################################################

################################################
# You don't need to touch anything below this. #
################################################

load_dotenv()
#TOKEN = os.environ['Token'] #Used for Testing Keep Commented
client = discord.Client()
bot = commands.Bot(command_prefix='!')

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

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
         return
    
    if message.content == 'mc!' or message.content == "Mc!":
      await message.channel.send(f"Scanning started: {ptime()}")
      
      server = MC("172.65.238.*",False,255,timeout)
      server = server.decode("utf-8")
      print(server)

      await message.channel.send(f"Testing the tool:\n{server}")

      await message.channel.send(f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds.")
      
      print(f"\nPing on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")
      #Real Stuff
      scan = MC(f"{lower_ip_bound}-{upper_ip_bound}",True,threads,timeout)

      scan = scan.decode("utf-8")

      await message.channel.send(f"It's Finally Dne!\n{scan}")
    elif "status!" in message.content:
      msg = message.content
      for i in "status!-":
        msg = msg.replace(i,"")
      print(msg)
      if msg == "":
        await message.channel.send("Usage, status!-255.255.255.255:25565")
      else:
        try:
          server = MinecraftServer.lookup(msg)
          status = server.status()
          mesg = "The server has {0} players and replied in {1} ms".format(status.players.online, status.latency)
          print(mesg)
          await message.channel.send(mesg)
        except:
          await message.channel.send(f"Failed to scan {msg}")

if __name__ == "__main__":
  client.run(TOKEN)