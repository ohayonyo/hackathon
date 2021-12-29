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
#import scapy.all as scapy
import logging
from questions import *

logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',datefmt='%H:%M:%S', level=logging.DEBUG)

udp_spam_time_lock = threading.Lock()

game_time_lock = threading.Lock()

length_of_spam_phase = 10
length_of_game_phase = 10

# Connection Data
host = '127.0.0.1'
# host = scapy.get_if_addr('eth1')
port = 2123
port_to_send_udp = 13117

# starting server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# server.bind((host, port))
server.bind((host, port))
port = server.getsockname()[1]
server.setblocking(False)
server.listen()

# Dictionnary of the clients
# looks like client: (team_name, score)
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
	for client in clients.keys(): # !@!@
		client.send(message)

# handling messages from clients
def handle(client):

	# get team name from client
	readers = [client]
	team_names=[]
	while readers:
		readable, writable, errored = select.select(readers, [], [], 0.5)
		
		for c in readable:
			try:
				team_name = c.recv(1024).decode('UTF-8')
				print("team_name:", team_name)
				team_names.append(team_name)
				clients[c] = (team_name, 0)
				print("Successfully added to client")
				
				if group1 == []:
					group1.append(team_name)
					print("Successfully added to group1")					
				elif group2 == []:
					group2.append(team_name)
					print("Successfully added to group2")

				readers.remove(c)

			except:
				#c.close()
				return

	# while not udp_spam_time_lock.locked():
	#     time.sleep(0.1)

	# actual game, this runs seperatly for each client but all at the same time! (different threads)
	
	print("group1", group1)
	print("group2", group2)
	if (group1==[]) and (group2==[]):
		print("No Participants GAME OVER")
		return
	# sending game announcement message
	game_announcement_string = "Welcome to Math Olympic Games for Dummies - or less than 6 yo kids :) -. \nGroup 1: \n== \n"
	print("game_announcement_string:", game_announcement_string)
	for name in group1:
		game_announcement_string = game_announcement_string + f'{name}\n'
	game_announcement_string = game_announcement_string + "Group 2: \n== \n"
	for name in group2:
		game_announcement_string = game_announcement_string + f'{name}\n'
	
	game_announcement_string = game_announcement_string + "\nGive the answer to this question as fast as you can!!\n\n" + output
	client.send(game_announcement_string.encode('UTF-8'))

	 #start 10 second counter thread
	 # logging.info(f'Starting and creating 10sec counting thread')

	print(f'{bcolors.OKGREEN}GAME STARTED!')

	readers = [client]

	while game_time_lock.locked() == True:
		print("\nWe are in the while game_time_lock.locked() == False:")
		#print("readers: ", readers)
		readable, writable, errored = select.select(readers, [], [], 0.5)
		print("readable", readable)
		print("writable", writable)
		for c in readable:
			try:
				print("c is", c)
				message = c.recv(16)
				print("received message:", message)
				if(message == b''):
					raise RuntimeError("Runtime Error !\nEmpty message")
				# print(f'{bcolors.OKBLUE}received "%s" \n' % message)
				# add 1 to the score of the scoring team
				result=check_question(message.decode('utf-8'), q_number)
				clients[c]=(clients[c][0],clients[c][1]+result)
			except:
				# index = clients.index(c)
				# clients.remove(c)
				# c.close()
				#team_name = team_names[index]
				
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
	print("locking the game_time_lock")
	game_time_lock.acquire()
	time.sleep(length_of_spam_phase)
	print("locking the udp_spam_lock")
	print("unlock the game_time_lock")
	udp_spam_time_lock.acquire()
	game_time_lock.release()
	time.sleep(length_of_game_phase)
	print("locking game_time_lock")
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
					# print("Connected with {}".format(str(address)))
					#start handling thread for client
					thread = threading.Thread(target=handle, args=(client,))
					thread.start()
					clients_threads.append(thread)
				else:
					pass
			except Exception as ex:
				# print("We got an exception when attempting to get tcp connection!!", ex.args)
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
		# logging.info(f'Starting and creating UDP spamming thread')
		udp_offer_thread = threading.Thread(target = send_offers_for_10_sec, args= ())
		if len(clients)<2 : 
			udp_offer_thread.start()

		# start 10 second counter thread
		# logging.info(f'Starting and creating 10sec counting thread')
		count_ten_seconds_thread = threading.Thread(target = count_ten_seconds)
		count_ten_seconds_thread.start()

		#accept connection
		recieve_tcp_connections()
		# print("Ten seconds finished")
		while not game_time_lock.locked():
			time.sleep(0.1)

		# close all client threads and remove them
		# logging.info(f'Starting to remove all client threads')
		for client_thread in clients_threads:
			client_thread.join()
			clients_threads.remove(client_thread)

		#close and remove client sockets and team names
		# logging.info(f'Started closing and removing all client sockets and team names')
		print(clients)

		# looks like -> teamname: 14
		teams=[]
		scores=[]
		#calculate the sum of all score by going through each client
		for c in clients:
			#getting the info out of each client
			teams.append(clients[c][0])
			scores.append(clients[c][1])


		#declare the winning group
		print("scores:", scores)
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

			# print out the name of the best team and their score
			# best_team_score = 0
			# best_team_name = ""
			
				# if score > best_team_score:
					# best_team_score = score
					# best_team_name = team

			# winning_team_declaration = winning_group_declaration + '\n\n' + f'The team that typed the most characters, and recieved the largest score is:\n==\n{best_team_name}\nWith the score of {best_team_score}\n\n'
			print("clients:", clients)
			print("We have "+ str(len(clients)) + "clients.")
			try:
				for c in clients:
					print("name:", clients[c][1])
					c.send(bytes(f'{bcolors.OKCYAN}{winning_group_declaration}','UTF-8'))
					print('sent')
					clients[c]=(clients[c][0],0)
					print('reset')
					c.close()
			
			except:
				print('in the except')
				pass

			clients.clear()
#			group1.clear()
#			group2.clear()
		# logging.info(f'Calling release of lock')

		#sleep for 10 seconds do nothing this is for testing
		# time.sleep(10)
		udp_spam_time_lock.release()
		game_time_lock.release()
		
		print(f'{bcolors.HEADER}Sending out offer requests...')

def send_offers_for_10_sec():
	# UDP_IP = ip
	# UDP_PORT = port

	udp_socket_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	udp_socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

	for i in range(0,length_of_spam_phase):
		for addr in offer_list:
			datagram = struct.pack('!IbH',0xabcddcba, 0x2, port)
			#udp_socket_out.send(datagram)
			udp_socket_out.sendto(datagram, addr) #'broadcast' instaead of addr?
			#udp_socket_out.sendto(datagram, '255.255.255.255') #broadcast instaead of addr?
			# sock_UDP.shutdown(socket.SHUT_RDWR)
		time.sleep(1)

	udp_socket_out.close()

def main():
	# our port
	offer_list.append(('127.0.0.1', 13117))
	# our teammate port
	offer_list.append(('127.0.0.1', 13117))

	mainLooper()

if __name__ == "__main__":
	main()
