from requests import get
import discord
from dotenv import load_dotenv
from discord.ext import commands
from mcstatus import MinecraftServer

load_dotenv()
TOKEN = 'ODc1NDQzMDY2ODQzMDM3NzA2.YRVl5A.Q8wnSeF76xkj0Z_Ptpjd53Om1Uk'

client = discord.Client()
bot = commands.Bot(command_prefix='!')

def MC():
    server = MinecraftServer.lookup("mc.hypixel.net:25565")
    status = server.status()
    print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
    query = server.query()
    print("The server has the following players online: {0}".format(", ".join(query.players.names)))
    return "The server has {0} players and replied in {1} ms".format(status.players.online, status.latency)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    ip = get('https://api.ipify.org').content.decode('utf8')

    if message.content == 'ip!':
        response = format(ip)
        await message.channel.send(response)
        print(response)
    elif message.content == 'whoami!':
        response = f'you are {message.author}'
        await message.channel.send(response)
        print(response)
    elif message.content == 'dm!':
        DM()
    elif message.content == 'mc!':
        print("MC ping started")
        
        def MC(ip):
            from mcstatus import MinecraftServer
            server = MinecraftServer.lookup(f"{ip}:25565")
            try:
                status = server.status()
                print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
                query = server.query()
                print("The server has the following players online: {0}".format(", ".join(query.players.names)))
                return "{ip}} has {0} players and replied in {1} ms".format(status.players.online, status.latency)
            except:
                return "Server is offline"
        
        print("test")
        server = MinecraftServer.lookup(f"{'mc.hypixel.net'}:25565")
        status = server.status()
        print("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
        await message.channel.send("The server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
            
        for a in range(255):
            for b in range(255):
                for i in range(255):
                    ip = f'172.{a}.{b}.{i}'
                    response = MC(ip)
                    if response == "Server is offline":
                        print(f"Server {ip} is offline")
                    else:
                        await message.channel.send(response)
                        print(response)
                await message.channel.send(f"192.{a}.{b}.xxx is scanned")

@bot.command()
async def DM(ctx, user: discord.User, *, message=None):
    message = message or "This Message is sent via DM"
    await user.send(message)

client.run(TOKEN)