''' KTN-project 2013 / 2014 Very simple server implementation that
should serve as a basis for implementing the chat server '''

import SocketServer
import json
import string
from datetime import datetime, time

'''
The RequestHandler class for our server.

It is instantiated once per connection to the server, and must
override the handle() method to implement communication to the
client.
'''

class ClientHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        global backlog
        global users
        # Get a reference to the socket object
        self.connection = self.request
        # Get the remote ip adress of the socket
        self.ip = self.client_address[0]
        # Get the remote port number of the socket
        self.port = self.client_address[1]
        print 'Client connected @' + self.ip + ':' + str(self.port)
        self.loggedIn = False
        self.username = ''
        while True:
            # Wait for data from the client
            data = json.loads(self.connection.recv(1024).strip())
            # Check if the data exists
            if data:
                print data
                self.response, _ = self.parse_client_data(data, backlog)
                print self.response
                self.send(self.response)
            else:
                users[self.username] = 0
                print 'Client disconnected!'
        self.connection.close()

    # Handles the incoming data from a client, and distributes it to the
    # appropriate client depending on the string i the request field
    def parse_client_data(self, data, backlog):
        request = string.lower(data['request'])
        response = {}
        loggedIn = False
        if request == 'login':
            self.username = data['username']
            response, self.loggedIn = self.validate_client(backlog)
        elif request == 'message':
            response = self.parse_message(data, backlog)
        elif request == 'logout':
            response, logout_success = self.validate_logout()
        else:
            # Report invalid request
            response = { 'response': 'Invalid request!' }
        return response, loggedIn

    # Validates a connecting client, checks login status and generates response
    def validate_client(self, backlog):
        global users
        response = { 'response': 'login', 'username': self.username }
        success = False
        if self.username.isalnum() != True:
            # Return error: invalid username
            print self.username
            response['error'] = 'Invalid username!'
            return response, success
        if self.username in users:
            if users[self.username] == 1:
                # Return error: name already taken
                response['error'] = 'Name already taken!'
            elif users[self.username] == 0:
                # Return login response, username and messages (from earlier?)
                response['messages'] = backlog
                users[self.username] = 1
                success = True
        elif self.username not in users:
            # Return login response, username (and messages?)
            response['messages'] = backlog
            users[self.username] = 1
            success = True
        if (self.loggedIn == False & success == True):
            self.loggedIn = True
        return response, success
        
    # Processes a received message and generates a response
    def parse_message(self, data, backlog):
        global users
        response = { 'response': 'message' }
        if self.loggedIn == False:
            response['error'] = 'You are not logged in!'
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = [ self.username, timestamp, data['message'] ]
            backlog.append(msg)
            response['message'] = msg
        return response

    def validate_logout(self):
        global backlog
        global users
        success = True
        response = { 'response': 'logout', 'username': self.username }
        if self.loggedIn == False:
            response['error'] = 'Not logged in!'
            success = False
        else:
            users[self.username] = 0
            self.loggedIn = False
            timestamp = datetime.now().strftime("%H:%M:%S")
            backlog.append([ self.username, timestamp, 'Logged out succesfully' ])
        return response, success
            

    # JSON-encodes and sends to this client
    def send(self, response):
        self.connection.sendall(json.dumps(response))
        
'''
This will make all Request handlers being called in its own thread.
Very important, otherwise only one client will be served at a time
'''


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class User:

    def __init__(self, username, ip):
        self.username = username
        self.ip = ip
        self.loggedIn = 0

    def __eq__(self, other):
        return self.username == other.username

    def set_login(self, status):
        self.loggedIn = status

    def set_ip(self, ip):
        self.ip = ip

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 9997
    backlog = [ ['username', '<timestamp>', 'test message one'] ]
    users = {'user1': '10.1.1.1', 'user2': '10.1.1.2'}
    

    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
