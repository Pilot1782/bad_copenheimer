# Bad Copenheimer

A Python impelentation of a discord bot that acts as a server scanner.

This is a discord bot that will scan ip adresses to see if they are minecraft servers and will post the results in your channel.

[Discord Server](https://discord.gg/kw3EYRwUkt) for testing a working and setup bot to see if it works for you.

----

## [Installation](https://github.com/Pilot1782/bad_copenheimer/wiki/Installation-(New-Bot))

[Installation Page](https://github.com/Pilot1782/bad_copenheimer/wiki/Installation-(New-Bot))

[Wiki](https://www.github.com/Pilot1782/bad_copenheimer/wiki)

[Troubleshooting](https://www.github.com/Pilot1782/bad_copenheimer/wiki/troubleshooting)

----

### Requirements

* Python 3.10 or higher
* Linux/Docker/WSL2 (for the scanner, the discord bot will run on windows)
* Masscan (for the scanner)
* requirements.txt
* node.js 16 or higher

### Usage

`/stats`
This will show you the stats of the databse.

![showcase](https://raw.githubusercontent.com/Pilot1782/bad_copenheimer/doc-resources/Screenshot_20221220_124016.png)

`/help`
This shows all of the commands you can use and their usage. Then to create your server list, run:

`/find`
This will look through your database to find servers that match the provided paramaters. In the new build, there are two more buttons that can be used to either show the player names and uuids of players found on the server or to pick another random server from the list, after pressing it, wait for the message to update.

![showcase](https://raw.githubusercontent.com/Pilot1782/bad_copenheimer/doc-resources/Screenshot_20230111_083824.png)

If the server has a whitelist the dot will be orange if it is online.

![showcase](https://raw.githubusercontent.com/Pilot1782/bad_copenheimer/doc-resources/Screenshot_20230222_034715.png)

#### Important

In order for /status to work properly the server should have enable-query=true in the server.properties file. This allows the server to brodcast who is currently logged onto the server.

----

## Help

Please check the wiki before posting an issue and read through the [troubleshooting](https://github.com/Pilot1782/bad_copenheimer/wiki/troubleshooting) first.

----

## Todo

Moved to [Project](https://github.com/users/Pilot1782/projects/1)
