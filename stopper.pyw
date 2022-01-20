import discord
import subprocess
import os
from discord.ext import commands
import json
import psutil

bot = commands.Bot(command_prefix='!',help_command=None)

settings_path = r"settings.json"
with open(settings_path, "r") as read_file:
  data = json.load(read_file)

TOKEN = data["token"]
os = data["os"]

def winkill():
  PROCNAME = "python.exe"

  for proc in psutil.process_iter():
      # check whether the process name matches
      if proc.name() == PROCNAME:
          proc.kill()
      else:
        print("No processes.")

def linkill():
  PROCNAME = "python"

  for proc in psutil.process_iter():
      # check whether the process name matches
      if proc.name() == PROCNAME:
          proc.kill()
      else:
        print("No processes.")

@bot.command(name="stop")
async def _stop(ctx):
  if os == 1:
    winkill()
  else:
    linkill()

if __name__ == "__main__":
  bot.run(TOKEN)