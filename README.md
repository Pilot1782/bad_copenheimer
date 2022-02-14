# Bad Copenheimer
A Python impelentation of a discord bot that acts as a server scanner.

This is a discord bot that will scan ip adresses to see if they are minecraft servers and will post the results in your channel.

## Installation
To install, clone the repository and run setup.pyw, then open settings.json. Then put your discord bot token into 'YOUR TOKEN HERE' and change any of the prefrences you would like.

To install the required packages run:
> python3 setup.python3

This installs all packages and update the paths in all files.

In order for the player finder to work, you need a ojang account. Put this in the settings.json file.

## Usage
The first time you use this bot, run 

>!help

This shows all of the commands you can use and their usage. Then to create your server list, run:

>!mc

This will get a list of all active minecraft servers, you may want to set the threads higher than the current value. This will take several hours to complete.

## Important

In order for !find and !status to work properly the server should have enable-query=true in the server.properties file

### All Possible Commands

>!help

>!find

>!status

>!mc

>!cscan


# Todo

**1:** Use send login packets to check is the server is whitelisted (Testing)

**2:** Create a [Meteor Client](https://github.com/MeteorDevelopment/meteor-client) addon and implement the scanner results into the addon allowing you to join servers based on "whitelist, modded, vinilla etc."

**3:** Add a webserver to request scan documents like the outputs.json so you can run this program on a raspi and leave it while using the server and discord to monitor and use the tool.