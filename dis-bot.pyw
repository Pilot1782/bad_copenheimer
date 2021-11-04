from requests import get
import discord
from dotenv import load_dotenv
from discord.ext import commands
import time
import os

load_dotenv()

##################################################
#Stuff for you to change
TOKEN = 'YOUR TOKEN HERE' #Your discord bot token
lower_ip_bound = "172.0.0.0" #Lowest is 10.0.0.0
upper_ip_bound = "192.255.255.255" #Highest is 199.255.255.255
threads = 255 #Max usable is 1000
timeout = 1000 #Ping timeout in miliseconds
path = r"qubo.jar" #Path to qubo.jar
##################################################

################################################
# You don't need to touch anything below this. #
################################################

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
      arr.append(f"{i}")
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

def MC(range,outp,threads,time):
  import subprocess
  ptime()
  print(f"Scanning {range} outputting {outp}")
  outp = subprocess.check_output(f"java -Dfile.encoding=UTF-8 -jar {path} -range {range} -ports 25565-25577 -th {threads} -ti {time}",shell=True)
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
      await message.channel.send(f"Scanning started: {ptime()}")
      print("MC ping started")
      
      print("Testing")
      #Test tool
      server = MC("172.65.238.*",True,255,timeout)
      await message.channel.send(f"Testing the tool: {server}")
      
      print(f"\nPing on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")
      #Real Stuff
      scan = MC(f"{lower_ip_bound}-{upper_ip_bound}",True,threads,timeout)

if __name__ == "__main__":
  client.run(TOKEN)