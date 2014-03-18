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
            if not data: break
            response, broadcast = self.parse_client_data(data)
            self.send(response, broadcast)
            print broadcast
            print response
            print server.users
        try:    
            del server.users[self.username]
        except:
            pass
        print "Client disconnected!"        
        self.connection.close()

    # Handles the incoming data from a client, and distributes it to the
    # appropriate client depending on the string i the request field
    def parse_client_data(self, data):
        broadcast = False
        request = string.lower(data['request'])
        response = {}
        if request == 'login':
            self.username = data['username']
            response = self.validate_login()
        elif request == 'message':
            response, broadcast = self.parse_message(data)
        elif request == 'logout':
            response = self.validate_logout()
        else:
            response = { 'response': 'Invalid request!' }
        return response, broadcast

    # Validates a connecting client, checks login status and generates response
    def validate_login(self):
        response = { 'response': 'login', 'username': self.username }
        if self.username.isalnum() != True:
            print self.username
            response['error'] = 'Invalid username!'
            return response
        if self.username in server.users:
            if self.loggedIn == True:
                response['error'] = 'Already logged in!'
            elif self.loggedIn == False:
                response['error'] = 'Name already taken!'
        elif self.username not in server.users:
            response['messages'] = server.backlog
            server.users[self.username] = self.request
            self.loggedIn = True
        return response
        
    # Processes a received message and generates a response
    def parse_message(self, data):
        response = { 'response': 'message' }
        if self.loggedIn == False:
            response['error'] = 'Not logged in!'
            broadcast = False
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = [ self.username, timestamp, data['message'] ]
            server.backlog.append(msg)
            response['message'] = msg
            broadcast = True
        return response, broadcast

    def validate_logout(self):
        response = { 'response': 'logout', 'username': self.username }
        if self.loggedIn == False:
            response['error'] = 'Not logged in!'
        else:
            self.loggedIn = False
            timestamp = datetime.now().strftime("%H:%M:%S")
            server.backlog.append([ self.username, timestamp, 'Logged out succesfully' ])
            try:
                del server.users[self.username]
            except:
                pass
        return response

    # JSON-encodes and sends to client or broadcast
    def send(self, response, broadcast):
        if broadcast == True:
            for username in server.users:
                server.users[username].sendall(json.dumps(response)) # Error here
                print "test1"
        elif broadcast == False:
            self.request.sendall(json.dumps(response))
                
'''
This will make all Request handlers being called in its own thread.
Very important, otherwise only one client will be served at a time
'''


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def init(self):
        self.backlog = [ ['username', '<timestamp>', 'test message one'] ]
        self.users = {}


if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 9997
    
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.init()

    server.serve_forever()
