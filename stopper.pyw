# This file will start a discord bot that only listens for the !stop command which will then kill all process that include the words python or python3

import multiprocessing
import os as osys
from discord.ext import commands
import json
import interactions
from funcs import *

settings_path = osys.getenv("PATH")

with open(settings_path) as json_file:
  data = json.load(json_file)
  if not data["testing"]:
    TOKEN = data["TOKEN"]
  else:
    TOKEN = osys.getenv("TOKEN")
  os = data["os"]

bot = interactions.Client(token=osys.getenv("TOKEN"))

@bot.command(
    name="stop",
    description="Stops the bot",
)
async def stop(ctx: interactions.CommandContext):
  print("BAIL|A*(&HDO#QDH")

if __name__ == "__main__":
  def step():
    time.sleep(0.1)
    print("step")
  proc = multiprocessing.Process(target=step)
  proc.start()
  bot.start()
  proc.join()