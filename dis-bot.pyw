from requests import get
import discord
from dotenv import load_dotenv
from discord.ext import commands
from mcstatus import MinecraftServer
import time

load_dotenv()
##################################################
#Stuff for you to change
TOKEN = 'YOUR TOKEN HERE' #Your discord bot token
lower_ip_bound = 172.0.0.0 #Lowest is 10.0.0.0
upper_ip_bound = 192.255.255.255 #Highest is 199.255.255.255
threads = 255 #Max usable is 1000
timeout = 1000 #Ping timeout in miliseconds
##################################################

###############################################
# You don't need to touch anything below this.#
###############################################

client = discord.Client()
bot = commands.Bot(command_prefix='!')

def ptime():
  x = 0
  for i in time.localtime():
    x = x + 1
    if x == 1:
      print(f"Year {i}")
    if x == 2:
      print(f"Month {i}")
    if x == 3:
      print(f"Day {i}")
    if x == 4:
      print(f"Hour {i}")
    if x == 5:
      print(f"Min {i}")

def MC(range,outp,threads,time):
  import subprocess
  ptime()
  print(f"Scanning {range} outputting {outp}")
  outp = subprocess.check_output(f"java -Dfile.encoding=UTF-8 -jar qubo.jar -range {range} -ports 25565-25577 -th {threads} -ti {time}",shell=True)
  if outp == True:
    print(outp)
    return outp

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content == 'mc!':
      await message.channel.send(f"Scanning started: {time.localtime()}")
      print("MC ping started")
      
      print("Testing")
      #Test tool
      server = MC("172.65.238.212",True,255,timeout)
      status = server.status()
      await message.channel.send(status)
      
      print(f"Ping on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")
      #Real Stuff
      scan = MC(f"{lower_ip_bound}-{upper_ip_bound}",True,threads,timeout)

if __name__ == "__main__":
  client.run(TOKEN)
