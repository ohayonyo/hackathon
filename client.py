import socket
import sys
import tty
import termios
import struct
import asyncio
import threading
import time
import select
import scapy.all as scapy
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

ip = scapy.get_if_addr('eth1')
UDP_port = 13117
COOKIE = 0xfeedbeef
MESSAGE_TYPE = 0x2
STRUCT_FORMAT = '!IbH'
CTRL_C = '\x03'
TEAM_NAME = 'Gal Dahan'

def rec_offer():
    print(f"{bcolors.HEADER}Client started, listening for offer requests... \n")

    # here we will do the recieving of udp

    sock_UDP = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock_UDP.bind((ip, UDP_port))

    data = sock_UDP.recvfrom(1024) # buffer size is 1024 bytes
    magic,mType,targetPort = struct.unpack(STRUCT_FORMAT,data[0])
    udp_ip = data[1][0]
    print(f"{bcolors.OKGREEN}Received offer from {udp_ip} attempting to connect  \n")

    if magic == COOKIE and mType == MESSAGE_TYPE:
        sock_UDP.close()
        try:
            connec_to_server(targetPort,udp_ip)
        except ConnectionRefusedError:
            rec_offer()
# end of UPD section @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ goku

# Connect the socket to the port where the server is listening

def connec_to_server(port, tip):
    sock_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (tip, port)
    print( f'{bcolors.HEADER}connecting to %s port %s \n' % server_address)
    ret = sock_TCP.connect(server_address)
    if ret == 0:
        print(f"{bcolors.FAIL}failed to connect to %s %s \n" %server_address)
        rec_offer()
    sock_TCP.setblocking(False)
    try:
        game_mode(sock_TCP)
    finally:
        readers = [sock_TCP]
        while readers:
            readable, writable, errored = select.select(readers, [], [], 0.5)
            for s in readable:
                data = s.recv(1024).decode('ascii')
                print(f'{bcolors.OKGREEN}{data}')
                readers.remove(s)

        print(f'{bcolors.FAIL}closing socket \n')
        sock_TCP.close()
        print(f'{bcolors.OKBLUE}Server  disconnected, listening for offer requests...')
        rec_offer()
def game_mode(socket):

    socket.sendall(bytes(TEAM_NAME,'UTF-8'))
    # sendThread = threading.Thread(target = rec, args =(socket))
    # receiveThread = threading.Thread(target = send, args =(socket))
    read = False
    for i in range(1,20):
        readable, writable, errored = select.select([socket], [], [],0.5)
        for s in readable:
            startMsg = socket.recv(1024).decode('ascii')
            print(f'{bcolors.OKGREEN} %s here' % startMsg)
            read = True
        if read: break
        time.sleep(0.5)

    readers = [socket]

    while readers:
        readable, writable, errored = select.select([socket], [socket], [],0.05)
        for w in writable:
            try:
                w.sendall(bytes(getch(),'UTF-8'))
            except:
                break

        if readable:
            return


def isData():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])



# Create a TCP/IP socket
def getch():
    tty.setcbreak(sys.stdin.fileno())
    fd = sys.stdin.fileno()
    # old = termios.tcgetattr(fd)
    old = termios.tcgetattr(sys.stdin)
    if(isData()):
        try:
            tty.setraw(fd)
            data = sys.stdin.read(1)
            if data == CTRL_C : sys.exit(0)
            return data
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


if __name__ == "__main__":
    rec_offer()