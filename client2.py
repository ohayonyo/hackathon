import socket
import sys
import keyboard
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

index=0
ip = scapy.get_if_addr('eth1')
#ip = '127.0.0.1'
UDP_port = 13117
COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
STRUCT_FORMAT = '!IbH'
CTRL_C = '\x03'
TEAM_NAME = 'Rabbin Hood 2.0'

def rec_offer():
	print(f"{bcolors.HEADER}Client started, listening for offer requests... \n")

	# Receiving a udp packet
	sock_UDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #SOCK_DGRAM is for UDP
	sock_UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	#print(ip)
	sock_UDP.bind((ip, UDP_port))

	data = sock_UDP.recvfrom(1024) # buffer size is 1024 bytes
	magic,mType,targetPort = struct.unpack(STRUCT_FORMAT,data[0])
	udp_ip = data[1][0]
	print(f"{bcolors.OKGREEN}Received offer from {udp_ip} attempting to connect...  \n")

	if magic == COOKIE and mType == MESSAGE_TYPE:
		sock_UDP.close()
		try:
			connec_to_server(targetPort,udp_ip)
		except ConnectionRefusedError:
			rec_offer()
# end of UPD section

# Connect the socket to the port where the server is listening

def connec_to_server(port, tip):
	print("connect to server")
	sock_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM is for TCP
	sock_TCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	server_address = ("172.1.0.123", 2123)
	
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
				data = s.recv(1024).decode('UTF-8')
				print(f'{bcolors.OKGREEN}{data}')
				readers.remove(s)

		print(f'{bcolors.FAIL}closing socket \n')
		sock_TCP.close()
		print(f'{bcolors.OKBLUE}Server  disconnected, listening for offer requests...')
		rec_offer()


def game_mode(socket):
	index=0
	socket.sendall(bytes(TEAM_NAME,'UTF-8'))
	read = False
	for i in range(1,20):
		readable, writable, errored = select.select([socket], [], [],0.5)
		for s in readable:
			startMsg = socket.recv(1024).decode('UTF-8')
			print(f'{bcolors.OKGREEN} %s here' % startMsg)
			read = True

		if read :
			break
		time.sleep(0.5)
	index+=1
	readers = [socket]
	while readers:
		readable, writable, errored = select.select([socket], [socket], [],0.05)
		#print("index=",index, "writable:\n", writable)
		for w in writable:
			try:
				print("Sending the answer...")
				x=w.sendall(bytes(acquire_digit(),'UTF-8'))
				#w.sendall(bytes(acquire_digit(),'UTF-8'))	
				print("Sent !", x)
			except:
				break

		if readable:
			return
		
		readers.remove(w)
		print('Finished the game')

# Create a TCP/IP socket
def getch():
	pressed=keyboard.record('enter')
	for i in pressed:
		for j in range(10):
			if str(i) == 'KeyboardEvent(' + str(j) + ' up)':
				print('sent !\n')
				return j
			
	return -1

def acquire_digit():
	a=input("Enter your answer here:\n")
	return a[-1]

if __name__ == "__main__":
	rec_offer()
