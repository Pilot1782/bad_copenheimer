# pyright: reportGeneralTypeIssues=false

from socket import socket, AF_INET, SOCK_STREAM
from sys import stderr, exit
from threading import Thread
from struct import pack, unpack, unpack_from, calcsize
import argparse

argparser = argparse.ArgumentParser(description="Minecraft chat bot")
argparser.add_argument("host", help="Server host", nargs="?")
argparser.add_argument("port", type=int, help="Server port", nargs="?")
argparser.add_argument("username", help="Username", nargs="?")
args = argparser.parse_args()

host = args.host if args.host else "localhost"
port = args.port if args.port else 25565
username = args.username if args.username else "pilot1782"

# Settings
debug = True  # Print all processed packets

# Set up the socket
sock = socket(AF_INET, SOCK_STREAM)
try:
    sock.connect((host, port))
    print("Connected to server")
except ConnectionRefusedError:
    print("Server is not online", file=stderr)
    exit(1)

# Data types
# https://gist.github.com/barneygale/1209061
def varint_pack(d):
    o = b''
    while True:
        b = d & 0x7F
        d >>= 7
        o += pack("B", b | (0x80 if d > 0 else 0))
        if d == 0:
            break
    return o
def varint_unpack(s):
    d, l = 0, 0
    length = len(s)
    if length > 5:
        length = 5
    for i in range(length):
        l += 1
        b = s[i]
        d |= (b & 0x7F) << 7 * i
        if not b & 0x80:
            break
    return (d, s[l:])

# Lots of packets have a varint in front of a value, saying how long it is.
def data_pack(data):
    return varint_pack(len(data)) + data
def data_unpack(bytes):
    length, bytes = varint_unpack(bytes)
    return bytes[:length], bytes[length:]

# Same as data_*, but encoding and decoding strings, because I'm lazy.
def string_pack(string):
    return data_pack(string.encode())
def string_unpack(bytes):
    string, rest = data_unpack(bytes)
    return string.decode("utf-8", "ignore"), rest

# Same as struct.unpack_from, but returns remaining data.
def struct_unpack(format, struct):
    data = unpack_from(format, struct)
    rest = struct[calcsize(format):]
    return data, rest

# Minecraft has a different set of packets depending on what it's doing.
# Only implemented handshake, login and play here, but status also exists.
mode = "handshake"
packets = {
    "send": {
        "handshake": {},
        "login": {},
        "play": {},
        "keep-alive": {}
    },
    "receive": {
        "login": {},
        "play": {}
    }
}
version = 758  # Minecraft 1.18.2

# Have I joined the game? (You can't chat before that)
joined = False

# Send packets
def send(packet, *args, **kwargs):
    func = packets["send"][mode][packet]
    packid = varint_pack(int(func.packid, 16))
    data = func(*args, **kwargs)
    sock.sendall(data_pack(packid + data))

# Receive packets
def receive(data=None):
    if isinstance(data, type(None)):
        data = sock.recv(1024)
    if not data:
        return
    data = data_unpack(data)[0]
    packid, data = varint_unpack(data)
    packid = str(hex(packid))
    packs = packets["receive"][mode]
    if packid not in packs:
        return
    packet = packs[packid]
    return packet.packname, packet(data)

# Packet decorator. This adds the functions for the packets to the dict.
def packet(direc, mode, packname, packid):
    def decor(func):
        if direc == "send":
            func.packid = packid
            packets[direc][mode][packname] = func
        elif direc == "receive":
            func.packname = packname
            packets[direc][mode][packid] = func
        return func
    return decor

# The packets
# http://wiki.vg/Protocol#Disconnect
# http://wiki.vg/Protocol#Disconnect_2
@packet("receive", "play", "disconnect", "0x40")
@packet("receive", "login", "disconnect", "0x0")
def _p(data):
    message = string_unpack(data)[0]

    print("Disconnected from server: " + message)
    return message

# http://wiki.vg/Protocol#Login_Success
@packet("receive", "login", "success", "0x2")
def _p(data):
    global mode
    mode = "play"

    uuid, data = string_unpack(data)
    name = string_unpack(data)[0]
    print("joined in as " + name)
    return uuid, name

# http://wiki.vg/Protocol#Keep_Alive
@packet("receive", "play", "keep-alive", "0x0")
def _p(data):
    try:
        id = unpack("!i", data)[0]
    except:
        print("Keep alive error")
        print(data)
        global stop
        stop = True
        return

    send("keep-alive", id)
    return id

# http://wiki.vg/Protocol#Join_Game
@packet("receive", "play", "joined", "0x1")
def _p(data):
    global joined
    joined = True

    stuff, data = struct_unpack('!iBbBB', data)
    level_type = string_unpack(data)[0]
    return stuff + (level_type, )

# http://wiki.vg/Protocol#Chat_Message
@packet("receive", "play", "chat", "0x2")
def _p(data):
    message = string_unpack(data)[0]

    # Insert parsing code here, I'm too lazy.
    print(message)
    return message

# http://wiki.vg/Protocol#Handshake
@packet("send", "handshake", "handshake", "0x0")
def _p(version, host, port, next):
    if next == 2:
        global mode
        mode = "login"

    version = varint_pack(version)
    host = string_pack(host)
    port = pack('!H', port)
    next = varint_pack(next)
    return version + host + port + next

# http://wiki.vg/Protocol#Login_Start
@packet("send", "login", "start", "0x0")
def _p(name):
    name = string_pack(name)
    return name

# http://wiki.vg/Protocol#Keep_Alive_2
@packet("send", "play", "keep-alive", "0x0")
def _p(id):
    id = pack('!i', id)
    return id

# http://wiki.vg/Protocol#Chat_Message_2
@packet("send", "play", "chat", "0x1")
def _p(message):
    message = string_pack(message)
    return message

stop = False

# Listen to incoming packets
def listen():
    global stop
    while not stop:
        data = sock.recv(1024)
        if not data:
            print("Connection Lost.",data)
            stop = True
        msg = receive(data)
        if debug and msg:
            print(msg)
Thread(target=listen).start()

# Login
send("handshake", version, host, port, 2)
send("start", username)


# Send chat messages
try:
    while not joined and not stop:
        pass
    while True:
        text = input()
        if stop:
            break
        send("chat", text)
except KeyboardInterrupt:
    if not stop:
        print("\nDisconnecting...")
        stop = True
