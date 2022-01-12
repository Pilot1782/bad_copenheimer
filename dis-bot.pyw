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


######################################################
#To change the settings, edit the settings.json file.#
######################################################

###############################################################
# Setting for Windows users and if you move the settings file #
###############################################################
settings_path = r"settings.json"

###############################
# Below this is preconfigured #
###############################

client = discord.Client()
bot = commands.Bot(command_prefix='!',help_command=None)
testing = False

if subprocess.check_output("whoami").decode("utf-8") != 'root\n' and os == 0:
  raise PermissionError(f"Please run as root, not as {subprocess.check_output('whoami').decode('utf-8')}")

with open(settings_path, "r") as read_file:
    data = json.load(read_file)

output_path = data["output-json"]
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
debug = data["debugging"]

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

def login(host,port,user,passwd):
  import struct
  import socket
  import time
  import urllib
  try:
    import urllib.request as urllib2
  except ImportError:
    import urllib2
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((host, port))

  logindata = {'user':username, 'password':passwd, 'version':'12'}
  data = urllib.urlencode(logindata)
  print('Sending data to login.minecraft.net...')
  req = urllib2.Request('https://login.minecraft.net', data)
  response = urllib2.urlopen(req)
  returndata = response.read() 
  returndata = returndata.split(":")
  mcsessionid = returndata[3]
  del req
  del returndata
  print("Session ID: " + mcsessionid)
  data = {'user':username,'host':host,'port':port}


  stringfmt = u'%(user)s;%(host)s:%(port)d'
  string = stringfmt % data
  structfmt = '>bh'
  packfmt = '>bih{}shiibBB'.format(len(enc_user))
  packetbytes = struct.pack(packfmt, 1, 23, len(data['user']), enc_user, 0, 0, 0, 0, 0, 0)
  s.send(packetbytes)
  connhash = s.recv(1024)
  print("Connection Hash: " + connhash)
  print('Sending data to http://session.minecraft.net/game/joinserver.jsp?user=JackBeePee&sessionId=' + mcsessionid + '&serverId=' + connhash + '...')
  req = urllib.urlopen('http://session.minecraft.net/game/joinserver.jsp?user=JackBeePee&sessionId=' + mcsessionid + '&serverId=' + connhash)
  returndata = req.read()
  if(returndata == 'OK'):
      print('session.minecraft.net says everything is okay, proceeding to send data to server.')
  else:
      print('Oops, something went wrong.')

  time.sleep(5)

  # All above here works perfectly.
  enc_user = data['user'].encode('utf-16BE')
  #This line is probably where something's going wrong:
  packetbytes = struct.pack('>bih', 1, 23, len(data['user'])) + data['user'].encode('utf-16BE') + struct.pack('>hiibBB', 2,0,0,0,0,0)
  print(len(packetbytes))
  print('Sending ' + packetbytes + ' to server.')
  s.send(packetbytes)

  while True:
      data = s.recv(1024)
      if data:
          print(data)

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
  print("Testing:{0}, Debugging:{1}\n".format(testing,debug))
  try:
    if testing:
      login('127.0.0.1',25565,'Pilot1782','Password')
    else:
      bot.run(TOKEN)
  except Exception as err:
    if debug:
      print("\n{0}".format(err))
    print("\nSorry, Execution of this file has failed.")