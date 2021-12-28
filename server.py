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

# Lists for clients
# List of client sockets
# dictionary of kind Socket: (str, int, int)
# looks like client: (team_name, score, group)
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
     # Request And Store Nickname
    # print("sned nameee")
    # client.send("Sned Mi TEEM name PLZ".encode('ascii'))

    # get team name from client
    readers = [client]
    while readers:
        readable, writable, errored = select.select(readers, [], [], 0.5)

        for c in readable:
            try:
                team_name = c.recv(1024).decode('ascii')
                # team_names.append(team_name)
                # clients.append(c)
                chosen_group = random.choice([1,2])
                clients[c] = (team_name, 0, chosen_group) #!@!@
                if chosen_group == 1:
                    group1.append(team_name)
                else:
                    group2.append(team_name)

                # print("Team Name is {}".format(team_name))
                readers.remove(c)

            except:
                # print("EXPPPPPPPP TEAM NAME PHASE")
                c.close()
                # print('{} Something is wrong with the given team name'.format(team_name).encode('ascii'))
                return

    while not udp_spam_time_lock.locked():
        time.sleep(0.1)


    # actual game, this runs seperatly for each client but all at the same time! (different threads)
    if (not group1) and (not group2):
        print("No Participants GAME OVER")
        return
    # sending game announcement message
    game_announcement_string = "Welcome to Keyboard Spamming Battle Royale. \nGroup 1: \n== \n"
    for name in group1:
        game_announcement_string = game_announcement_string + f'{name}\n'
    game_announcement_string = game_announcement_string + "Group 2: \n== \n"
    for name in group2:
        game_announcement_string = game_announcement_string + f'{name}\n'
    game_announcement_string = game_announcement_string + "\nStart pressing keys on your keyboard as fast as you can!!"
    client.send(game_announcement_string.encode('ascii'))

     #start 10 second counter thread
     # logging.info(f'Starting and creating 10sec counting thread')

    print(f'{bcolors.OKGREEN}GAME STARTED!')



    readers = [client]



    while game_time_lock.locked() == False:
        readable, writable, errored = select.select(readers, [], [], 0.5)

        for c in readable:
            try:
                message = c.recv(16)
                if(message == b''):
                    raise RuntimeError("Runtime Error !\nEmpty message")
                # print(f'{bcolors.OKBLUE}received "%s" \n' % message)
                # add 1 to the score of the scoring team
                x = clients[c]
                y = list(x)
                y[1] = y[1] + 1
                x = tuple(y)
                clients[c] = x
            except:
                # index = clients.index(c)
                # clients.remove(c)
                # c.close()
                # team_name = team_names[index]
                # team_names.remove(team_name)
                # print("EXPPPPPPPP GAME")
                team_name = clients[c][0] #!@!@
                del clients[c]
                c.close
                # print('{} left!'.format(team_name).encode('ascii'))

                break


    # logging.info(f'{bcolors.OKCYAN} Quiting client!! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')



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
                    # print("Connected with {}".format(str(address)))
                    # logging.info(f'Connected with :{address}')
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
    while True:

        # start UDP spammer thread
        # logging.info(f'Starting and creating UDP spamming thread')
        udp_offer_thread = threading.Thread(target = send_offers_for_10_sec, args= ())
        udp_offer_thread.start()

        # start 10 second counter thread
        # logging.info(f'Starting and creating 10sec counting thread')
        count_ten_seconds_thread = threading.Thread(target = count_ten_seconds)
        count_ten_seconds_thread.start()

        #accept connection
        # logging.info(f'Calling recieve_tcp_connections func')
        recieve_tcp_connections()
        # logging.info(f'Came back from recieve_tcp_connections func')

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
        # print(clients)

        # looks like -> teamname: 14
        score_by_teamname = {}
        #counters for the score of each group, to see who won
        group1_score = 0
        group2_score = 0
        #calculate the sum of all score by going through each client
        for c in clients:
            #getting the info out of each client
            team_name = clients[c][0] # !@!@
            score = clients[c][1]
            group = clients[c][2]
            score_by_teamname[team_name] = score
            if group == 1:
                group1_score += score
            else:
                group2_score += score
            # del clients[c]
            # close the socket of the team as it is not needed anymore


        #declare the winning group

        winning_group_decleration = f'Game over! \nGroup 1 typed in {group1_score} characters. Group 2 typed in {group2_score} characters.'

        if group1_score > group2_score:
            winning_group_decleration += "Group 1 wins!\n\nCongratulations to the winners:\n==\n"
            for name in group1:
                winning_group_decleration += f'{name}\n'
        elif group2_score > group1_score:
            winning_group_decleration += "Group 2 wins!\n\nCongratulations to the winners:\n==\n"
            for name in group2:
                winning_group_decleration += f'{name}\n'
        else:
            winning_group_decleration += "The game is a draw. No one wins..\n\nCongratulations to everyone!!"

        print(f'{bcolors.OKGREEN}{winning_group_decleration}\n\n')

        # print out the name of the best team and their score
        best_team_score = 0
        best_team_name = ""
        for team, score in score_by_teamname.items():
            if score > best_team_score:
                best_team_score = score
                best_team_name = team

        winning_team_declaration = winning_group_decleration + '\n\n' + f'The team that typed the most characters, and recieved the largert score is:\n==\n{best_team_name}\nWith the score of {best_team_score}\n\n'
        for c in clients:
            c.send(bytes(f'{bcolors.OKCYAN}{winning_team_declaration}','ascii'))
            c.close()


        clients.clear()
        group1.clear()
        group2.clear()
        # logging.info(f'Calling release of lock')

        #sleep for 10 seconds do nothing this is for testing
        # time.sleep(10)
        udp_spam_time_lock.release()
        game_time_lock.release()
        print(f'{bcolors.HEADER}Game over, sending out offer requests...')


def send_offers_for_10_sec():
    # UDP_IP = ip
    # UDP_PORT = port

    udp_socket_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    udp_socket_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    for i in range(0,length_of_spam_phase):
        for addr in offer_list:
            datagram = struct.pack('!IbH',0xabcddcba, 0x2, port)
            # print(f"{bcolors.OKCYAN}\nSending UDP packet to address {addr} with message {datagram}")
            # # print(f"{bcolors.HEADER}UDP target IP: %s \n" % port_to_send_udp)
            # # print(f"{bcolors.HEADER}UDP target port: %s \n" % port_to_send_udp)
            # # print(f"{bcolors.OKCYAN}message: %s \n" % datagram)
            udp_socket_out.sendto(datagram, addr)
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