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
                self.response, _ = self.parse_client_data(data)
                print self.response
                self.send(self.response)
            else:
                del server.users[self.username]
                print 'Client disconnected!'
        self.connection.close()

    # Handles the incoming data from a client, and distributes it to the
    # appropriate client depending on the string i the request field
    def parse_client_data(self, data):
        request = string.lower(data['request'])
        response = {}
        loggedIn = False
        if request == 'login':
            self.username = data['username']
            response, self.loggedIn = self.validate_client()
        elif request == 'message':
            response = self.parse_message(data)
        elif request == 'logout':
            response, logout_success = self.validate_logout()
        else:
            # Report invalid request
            response = { 'response': 'Invalid request!' }
        return response, loggedIn

    # Validates a connecting client, checks login status and generates response
    def validate_client(self):
        response = { 'response': 'login', 'username': self.username }
        success = False
        if self.username.isalnum() != True:
            # Return error: invalid username
            print self.username
            response['error'] = 'Invalid username!'
            return response, success
        if self.username in server.users:
            # Return error: name already taken
            response['error'] = 'Name already taken!'
        elif self.username not in server.users:
            # Return login response, username (and messages?)
            response['messages'] = server.backlog
            success = True
        if (self.loggedIn == False & success == True):
            self.loggedIn = True
        return response, success
        
    # Processes a received message and generates a response
    def parse_message(self, data):
        response = { 'response': 'message' }
        if self.loggedIn == False:
            response['error'] = 'You are not logged in!'
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = [ self.username, timestamp, data['message'] ]
            server.backlog.append(msg)
            response['message'] = msg
        return response

    def validate_logout(self):
        success = True
        response = { 'response': 'logout', 'username': self.username }
        if self.loggedIn == False:
            response['error'] = 'Not logged in!'
            success = False
        else:
            self.loggedIn = False
            timestamp = datetime.now().strftime("%H:%M:%S")
            server.backlog.append([ self.username, timestamp, 'Logged out succesfully' ])
            del server.users[self.username]
        return response, success        

    # JSON-encodes and responds to current client
    def send(self, response):
        self.connection.sendall(json.dumps(response))

    def broadcast(self, data):
        for username in server.users:
            server.users[username].sendall(json.dumps(data))
        
'''
This will make all Request handlers being called in its own thread.
Very important, otherwise only one client will be served at a time
'''


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def init(self):
        self.backlog = [ ['username', '<timestamp>', 'test message one'] ]
        self.users = { 'user1': '10.1.1.1', 'user2': '10.1.1.2' }


if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 9997
    
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.init()

    server.serve_forever()
