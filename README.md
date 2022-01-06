# Bad Copenheimer
A Python impelentation of a discord bot that acts as a server scanner.

This is a discord bot that will scan ip adresses to see if they are minecraft servers and will post the results in your channel.

# Installation
To insatll, clone the repository and run setup.pyw,then open dis-bot.pyw. Then put your discord bot token into 'YOUR TOKEN HERE' and change any of the prefrences you would like.

# Usage
The first time you use this bot, run 

>!help

This shows all of the commands you can use and their usage. Then to create your server list, run:

>!mc

This will get a list of all active minecraft servers, you may want to set the threads higher than the current value. This will take several hours to complete.

### Important

In order for !find and !status to work properly the server should have enable-query=true in the server.properties file

### All Possible Commands

>!help

>!find

>!status

>!mc

>!cscan

These are all of the possible commands implemented so far.


# Todo

**1:** Store server information into a json instead of .txt files. (WIP)

**2:** Make a single message that shows the status of all known minecraft servers.

**3:** Optimize (implement masscan) (done)

**4:** Use a minecraft client to send login packets to check is the server is whitelisted (Reasherching)