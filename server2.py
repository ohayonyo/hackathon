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

import socket
import threading
import time
import struct
import select
import random
import scapy.all as scapy
import logging
from questions import *

logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',datefmt='%H:%M:%S', level=logging.DEBUG)

udp_spam_time_lock = threading.Lock()

game_time_lock = threading.Lock()

length_of_spam_phase = 10
length_of_game_phase = 10

# Connection Data
# host = '127.0.0.1'
host = scapy.get_if_addr('eth1')
port = 2123
# port_to_send_udp = 13117

# starting server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

server.bind((host, port))
port = server.getsockname()[1]
server.setblocking(False)
server.listen()

# Dictionnary of the clients
# looks like <client: (team_name, score)>
clients = {}

# Lists for the groups, each list holds the names of the teams in the groups
group1 = []
group2 = []

# List of addresses to which we should send offer messages to
offer_list = []

# for testing we make client thread lists
clients_threads = []

# send message to all clients
def broadcast(message):
	for client in clients.keys():
		client.send(message)

# handling messages from clients
def handle(client):
	
	can_win=True
	# get team name from client
	readers = [client]
	team_names=[]
	while readers:
		readable, writable, errored = select.select(readers, [], [], 0.5)
		
		for c in readable:
			try:
				team_name = c.recv(1024).decode('UTF-8')
				team_names.append(team_name)
				clients[c] = (team_name, 0)
				
				if group1 == []:
					group1.append(team_name)
					print("Successfully added to group1")					
				elif group2 == []:
					group2.append(team_name)
					print("Successfully added to group2")

				readers.remove(c)

			except:
				return

	if (group1==[]) and (group2==[]):
		print("No Participants GAME OVER")
		return
	# sending game announcement message
	game_announcement_string = "Welcome to Math Olympic Games for Dummies - or less than 6 yo kids :) -. \nGroup 1: \n== \n"
	for name in group1:
		game_announcement_string = game_announcement_string + f'{name}\n'
	game_announcement_string = game_announcement_string + "Group 2: \n== \n"
	for name in group2:
		game_announcement_string = game_announcement_string + f'{name}\n'
	
	game_announcement_string = game_announcement_string + "\nGive the answer to this question as fast as you can!!\n\n" + output
	client.send(game_announcement_string.encode('UTF-8'))

	print(f'{bcolors.OKGREEN}GAME STARTED!')

	readers = [client]

	while game_time_lock.locked() == True:
		readable, writable, errored = select.select(readers, [], [], 0.5)
		for c in readable:
			try:
				message = c.recv(16)
				if(message == b''):
					raise RuntimeError("Runtime Error !\nEmpty message")
				result=check_question(message.decode('utf-8'), q_number)
				print("the result is: ", result)
				print("can_win:", can_win)
				if can_win:
					print('clients[c]=', clients[c])
					clients[c]=(clients[c][0],clients[c][1]+result)
					if result==1:
						can_win = False
					else:
						can_win = True
			except:			
				print("NOT WORKING PROPERLY")
				team_name = clients[c][0]
				del clients[c]
				c.close
				print('{} left!'.format(team_name).encode('UTF-8'))
				team_names.remove(team_name)
				break


	# logging.info(f'{bcolors.OKCYAN} Quiting client!! @')


#counting 10 seconds
def count_ten_seconds ():
	game_time_lock.acquire()
	time.sleep(length_of_spam_phase)
	udp_spam_time_lock.acquire()
	game_time_lock.release()
	time.sleep(length_of_game_phase)
	game_time_lock.acquire()

def recieve_tcp_connections():
	# logging.info(f'Entered recieve_tcp_connections func')
	readers = [server]

	while udp_spam_time_lock.locked() == False:
		readable, writable, errored = select.select(readers, [], [], 0.5)

		for s in readable:
			try:
				if s == server:
					client, address = s.accept()
					thread = threading.Thread(target=handle, args=(client,))
					thread.start()
					clients_threads.append(thread)
				else:
					pass
			except Exception as ex:
				pass
			finally:
				pass

# recieving / listening function
def mainLooper():
	# logging.info(f'Entered MainLopper func')
	print(f'{bcolors.HEADER} Server started, listening on IP address {host}')
	looper = True
	while looper:
		global output, q_number
		(output,q_number)=generate_question()
		# start UDP spammer thread
		udp_offer_thread = threading.Thread(target = send_offers_for_10_sec, args= ())
		if len(clients)<2 : 
			udp_offer_thread.start()

		# start 10 second counter thread
		count_ten_seconds_thread = threading.Thread(target = count_ten_seconds)
		count_ten_seconds_thread.start()

		#accept connection
		recieve_tcp_connections()
		while not game_time_lock.locked():
			time.sleep(0.1)

		# close all client threads and remove them
		for client_thread in clients_threads:
			client_thread.join()
			clients_threads.remove(client_thread)

		teams=[]
		scores=[]
		
		for c in clients:
			#getting the info out of each client
			teams.append(clients[c][0])
			scores.append(clients[c][1])


		#declare the winning group
		if group1!=[] and group2!=[]:
			try:
				winning_group_declaration = f'Game over! \nTeam 1 typed in {scores[0]} characters. Team 2 typed in {scores[1]} characters.'
				if scores[0] > scores[1]:
					winning_group_declaration += "Team 1 wins!\n\nCongratulations to the winners:\n==\n"
					winning_group_declaration += f'{teams[0]}\n'
				elif scores[1] > scores[0]:
					winning_group_declaration += "Team 2 wins!\n\nCongratulations to the winners:\n==\n"
					for name in group2:
						winning_group_declaration += f'{teams[1]}\n'
				else:
					winning_group_declaration += "The game is a draw. No one wins..\n\nCongratulations to everyone!!"
			except:
				winning_group_declaration= "Nobody won :("
			print(f'{bcolors.OKGREEN}{winning_group_declaration}\n\n')

			try:
				for c in clients:
					c.send(bytes(f'{bcolors.OKCYAN}{winning_group_declaration}','UTF-8'))
					clients[c]=(clients[c][0],0)
					c.close()
			
			except:
				pass

			clients.clear()

		udp_spam_time_lock.release()
		game_time_lock.release()
		
		print(f'{bcolors.HEADER}Sending out offer requests...')

def send_offers_for_10_sec():

	udp_socket_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	udp_socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	udp_socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	for i in range(0,length_of_spam_phase):
		datagram = struct.pack('!IbH',0xabcddcba, 0x2, port)
		udp_socket_out.sendto(datagram, ('broadcast',13117))	
		time.sleep(1)

	udp_socket_out.close()

def main():
	# # our port
	offer_list.append(('255.255.255.255', 13117))
	# # our teammate port
	# offer_list.append(('127.0.0.1', 13117))

	mainLooper()

if __name__ == "__main__":
	main()
