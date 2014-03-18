'''
KTN-project 2013 / 2014
'''
from workers import *
import time
import socket
import json
import errno


class Client(object):

    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.loggedIn = False

    def start(self, host, port):
        self.connection.connect((host, port))
        
    # Receives incoming data from listener-thread and generates ouput to console
    def parse_server_data(self):
        while True:
            try:
                data_json = self.connection.recv(1024)
            except socket.error as error:
                if error.errno == errno.ECONNRESET:
                    print "Connection closed by server."
                    self.force_disconnect()
            except:
                return
            
            else:
                try:
                    data = json.loads(data_json)
                    self.generate_output(data)
                    print userInput
                    #print data
                    #print '\n'
                except:
                    pass


    def generate_output(self, data):
        if data['response'] == 'login':
            if 'error' in data:
                print data['error'] + '\n'
                self.loggedIn = False
            else:
                self.print_backlog(data['message'])
                self.loggedIn = True
        elif data['response'] == 'message':
            if 'error' in data:
                print data['error'] + '\n'
            else:
                self.print_message(data['message'])
        elif data['response'] == 'logout':
            if 'error' in data:
                print data['error'] + '\n'
            else:
                print 'User ' + self.username + ' was logged out succesfully.\n'

    def print_message(self, msg):
        print '<' + msg[0] + ' said @ ' + msg[1] + '> ' + msg[2] + '\n'

    # Todo
    def print_backlog(self, log):
        print "Login successful, printing messages this session...\n"
        for message in range(len(log)):
            print message[0] + '% ' + 'said @ ' + message[1] + ':' + ' ' + message[2]

        
    def close_connection(self, connection):
        print 'Connection closed'
        self.connection.close()

    def send(self, data):
        self.connection.sendall(json.dumps(data))
        #print data

    def force_disconnect(self):
        self.connection.close()
        self.isLoggedin = False

    def login(self):
        data = { 'request': 'login', 'username': self.username }
        self.send(data)

    def logout(self):
        data = { 'request': 'logout' }
        self.send(data)

    def handle_input(self):
        userInput = raw_input('Enter message: ');
        valid, error, inputList = self.validate_input(userInput)
        if valid == False:
            print error
            return
        if inputList[0].lower() == 'login':
            self.username = inputList[1]
            self.login()
        elif inputList[0].lower() == 'logout':
            self.logout()
        else:
            return { 'request': 'message', 'message': userInput }

        # Funksjon for aa sjekke om user input er gyldig foer f.eks login() kan kalles
    def validate_input(self, s):
        ok = True
        strLst = s.lower().split()
        err = "Invalid input: "
        if s.split() == []:
            ok, err = False, err + "No characters entered, please enter a message...\n"
        elif (strLst[0].lower() == 'login') & (len(strLst) < 2):
            if self.loggedIn == True:
                ok, err = False, "Already logged in!\n"
            elif self.loggedIn == False:
                ok, err = False, err + "Please enter a username...\n"
        return ok, err, strLst


if __name__ == "__main__":
    client = Client()
    client.start('localhost', 9997)
    # Thread for handling and parsing received data
    receiver = ReceiveMessageWorker(client)
    receiver.start()
    # Thread for taking input and sending data
    sender = SendMessageWorker(client)
    sender.start()
