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
        # Get a reference to the socket object
        self.connection = self.request
        # Get the remote ip adress of the socket
        self.ip = self.client_address[0]
        # Get the remote port number of the socket
        self.port = self.client_address[1]
        print 'Client connected @' + self.ip + ':' + str(self.port)
        self.login = False
        self.response = { 'asdf': 'test' }
        self.username = ''
        while True:
            # Wait for data from the client
            data = json.loads(self.connection.recv(1024).strip())
            # Check if the data exists
            if data:
                print data
                self.response, self.login = self.parse_client_data(data, backlog)
                self.send(self.response)
            else:
                print 'Client disconnected!'
        self.connection.close()

    # Handles the incoming data from a client, and distributes it to the
    # appropriate client depending on the string i the request field
    def parse_client_data(self, data, backlog):
        request = string.lower(data['request'])
        print request
        response = {}
        login = False
        if request == 'login':
            response, login = self.validate_client(backlog)
        elif request == 'message':
            response = self.parse_message(data, backlog)
        elif request == 'logout':
            response, success = self.validate_logout()
        else:
            # Report invalid request
            pass
        return response, login

    # Validates a connecting client, checks login status and generates response
    def validate_client(self, backlog):
        global users
        result = { 'response': 'login', 'username': self.username }
        success = False
        if self.username.isalnum() != True:
            # Return error: invalid username
            result['error'] = 'Invalid username!'
        if self.username in users:
            if users[self.username] == 1:
                # Return error: name already taken
                result['error'] = 'Name already taken!'
            elif users[self.username] == 0:
                # Return login response, username and messages (from earlier?)
                result['messages'] = backlog
                users[self.username] = 1
                success = True
        elif self.username not in users:
            # Return login response, username (and messages?)
            result['messages'] = backlog
            users[self.username] = 1
            success = True
        return result, success
        
    # Processes a received message and generates a response
    def parse_message(self, data, backlog):
        global users
        response = { 'response': 'message' }
        if self.login == False:
            response['error'] = 'You are not logged in!'
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = [ self.username, timestamp, data['message'] ]
            backlog.append(msg)
            response['message'] = msg
        return response

    def validate_logout(self):
        success = True
        response = { 'response': 'logout', 'username': self.username }
        if self.login == False:
            response['error'] = 'Not logged in!'
            success = False
        return response, success
            
        

    # JSON-encodes and broadcasts message to all logged in clients
    def send(self, response):
        self.connection.sendall(json.dumps(response))
'''
This will make all Request handlers being called in its own thread.
Very important, otherwise only one client will be served at a time
'''


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 9997
    backlog = [ ['username', '<timestamp>', 'test message one'] ]
    users = { 'user1': 1, 'user2': 0 }

    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
