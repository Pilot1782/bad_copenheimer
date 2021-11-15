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
TOKEN = 'YOUR TOKEN HEREE' #Your discord bot token
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
bot = commands.Bot(command_prefix='!')
testing = False

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
    outpt = subprocess.check_output("dir",shell=True)
  outpt = outpt.decode("utf-8")
  outpt = outpt.split('\n')
  return outpt
  

def find(player):
  files = file_out()
  outp = []
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
        outp.append(ip_addr)
  
  for i in outp:
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
      print(f"quering isn't supported on {i}")

def testing():
  if testing:
    print(find(''))

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
         return
    
    #Command MC
    if message.content.lower() == 'mc!':
      await message.channel.send(f"Scanning started: {ptime()}")
      
      server = MC("172.65.238.*",False,255,timeout)
      server = server.decode("utf-8")
      print(server)

      await message.channel.send(f"Testing the tool:\n{server}")

      await message.channel.send(f"\nStarting the scan at {ptime()}\nPinging {lower_ip_bound} through {upper_ip_bound}, using {threads} threads and timingout after {timeout} miliseconds.")
      
      print(f"\nPing on {lower_ip_bound} through {upper_ip_bound}, with {threads} threads and timeout of {timeout}")
      
      scan = MC(f"{lower_ip_bound}-{upper_ip_bound}",True,threads,timeout)

      scan = scan.decode("utf-8")

      await message.channel.send(f"\nIt's Finally Done!\n\n{scan}")
    
    #Command STATUS
    elif "status!" in message.content.lower():
      msg = message.content
      for i in "status!-":
        msg = msg.replace(i,"",1)

      print(f"Scan of {msg} requested.")
      
      if msg == "":
        await message.channel.send("Usage, status!-255.255.255.255:25565")
      
      else:
        try: #Try getting the status
          server = MinecraftServer.lookup(msg)
          status = server.status()
          mesg = "The server has {0} players and replied in {1} ms\n".format(status.players.online, status.latency)
          print(mesg)
          await message.channel.send(mesg)
        except:
          await message.channel.send(f"Failed to scan {msg}.\n")
          print(f"Failed to scan {msg}.\n")
        
        try: #Try quering server
          server = MinecraftServer.lookup(msg)
          query = server.query()
          print("The server has the following players online: {0}".format(", ".join(query.players.names)))
          await message.channel.send("The server has the following players online: {0}".format(", ".join(query.players.names)))
        except:
          print(f"Failed to query {msg}")
          await message.channel.send(f"Failed to query {msg}.")

    elif "find!" in message.content.lower(): #Find command
      msg = message.content
      for i in "find!-":
        msg.replace(i,"",1)
      await message.channel.send(find(msg))


if __name__ == "__main__":
  testing()
  client.run(TOKEN)