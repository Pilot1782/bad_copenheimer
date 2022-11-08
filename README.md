-----

# Bad Copenheimer
A Python impelentation of a discord bot that acts as a server scanner.

This is a discord bot that will scan ip adresses to see if they are minecraft servers and will post the results in your channel.

## Installation

[Installation Page](https://www.github.com/Pilot1782/bad_copenheimer/wiki/Installation)

## Usage

### Experimental
This branch contains a new file, `scanCore.ipynb` this requires that you have masscan installed and a mongodb database setup and must be run in linux or with a docker container, but will run much faster than the current method and store your servers into an easy to sort database.

### Normal

`/help`
This shows all of the commands you can use and their usage. Then to create your server list, run:

`/server_scan`
This will get a list of all active minecraft servers, you may want to set the threads higher than the current value. This will take several hours to complete.

`/status`
This will get information about the requested server, including players online, ping, and if possible players connected.

#### Important

In order for /status to work properly the server should have enable-query=true in the server.properties file. This allows the server to brodcast who is currently logged onto the server.

## Help

Please check the wiki before posting an issue and read through the [troubleshooting](https://github.com/Pilot1782/bad_copenheimer/wiki/troubleshooting) first.

# Todo

Moved to [Project](https://github.com/users/Pilot1782/projects/1)
