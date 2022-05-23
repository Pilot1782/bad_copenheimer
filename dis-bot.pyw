import interactions
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
bot = interactions.Client(token=osys.getenv("TOKEN"))

with open(settings_path, "r") as read_file: # Open the settings file and start defineing variables from it
  data = json.load(read_file)

testing = data["testing"] #bc it easier
home_dir = data["home-dir"]
output_path = home_dir + "outputs.json"
usr_name = data["user"]
if not testing:
  TOKEN = data["TOKEN"]
  guildid = data["guild-id"]
else:
  guildid = osys.getenv("GUILDID")
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
@bot.command(
    name="server_scan",
    description="scan some ips",
    options = [
        interactions.Option(
            name="text",
            description="What you want to say",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def server_scan(ctx: interactions.CommandContext, ip_lower_bound: str, ip_upper_bound: str):
  iplower = ip_lower_bound
  ipupper = ip_upper_bound
  log("Command: mc run" + iplower + "|" + ipupper)

  if ipupper != None:
    lower_ip_bound = iplower
    upper_ip_bound = ipupper
  
    testar = iplower.split(".")
    if len(testar) != 4:
      await ctx.send("Invalid IP")
      exit()
    testar = ipupper.split(".")
    if len(testar) != 4:
      await ctx.send("Invalid IP")
      exit()

  for line in scan(lower_ip_bound, upper_ip_bound):
    await ctx.send(line)


    
@bot.command(
 name="status",
 description="Check the status of the given ip or check all in the json file",
 options=[
    interactions.Option(
        name="ip",
        description="The ips to check, seperated by a space, ie 'ip1 ip2 ip3'",
        required=False,
        type = interactions.OptionType.STRING,
    ),
 ],
)
async def status(ctx: interactions.CommandContext, ip: str):
# Get the status of a specified server or all of the saved servers

  if len(ip) > 0:
    print(f"Scan of {ip} requested.")
    log(f"Scan of {ip} requested.")
    for i in ip.split(" "):
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

#Help command
@bot.command(
    name="help",
    description="Show the help message",
)
async def help(ctx: interactions.CommandContext):
  await ctx.send("""
########################################################
/server scan <ip_lower_bound> <ip_upper_bound>
scans the ip range and returns the status of the servers

/server status <ip>
returns the status of the server

/server help
shows this message
########################################################
""")

#Startup
def startup():
  bot.start()

# Print whether debugging and testing are active
if __name__ == "__main__":
  print("Testing:{0}, Debugging:{1}\n".format(testing,debug))
  log("Startup has been called, "+str(testing)+": testing and "+str(debug)+": debugging")
  try:
    if testing:
      flag = True
      dprint("Starting bot...")
      proc2 = multiprocessing.Process(target=startup,args=())
      proc2.start()

      if os == 1:
        pypath = r"%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
      else:
        pypath = "python3"
      
      dprint("Starting emergency bot...")
      for line in run_command(r"{} stopper.pyw".format(pypath)):
        print(line.decode("utf-8"))
        if line.decode("utf-8") == "BAIL|A*(&HDO#QDH" and proc2.is_alive():
          proc2.terminate()
          print("Stopped")
          break

      proc2.join()
    else:
      flag = True
      dprint("Starting bot...")
      proc2 = multiprocessing.Process(target=startup,args=())
      proc2.start()

      if os == 1:
        pypath = r"%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
      else:
        pypath = "python3"
      
      dprint("Starting emergency bot...")
      for line in run_command(r"{} stopper.pyw".format(pypath)):
        print(line.decode("utf-8"))
        if line.decode("utf-8") == "BAIL|A*(&HDO#QDH" and proc2.is_alive():
          proc2.terminate()
          print("Stopped")
          break

      proc2.join()
  except Exception as err:
    print("\n\nSorry, Execution of this file has failed, see the log for more details.\n")
    log(err)