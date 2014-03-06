''' KTN-project 2013 / 2014 Very simple server implementation that
should serve as a basis for implementing the chat server '''

import SocketServer
import json
import string
import time

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
        while True:
            # Wait for data from the client
            data = json.loads(self.connection.recv(1024).strip())
            # Validate request type and handle data
            # Check if the data exists
            if data:
                print data
                #self.connection.sendall(json.dumps(data))
                response = self.parse_client_data(data, backlog)
                self.send(response)
            else:
                print 'Client disconnected!'
        self.connection.close()

    # Handles the incoming data from client
    def parse_client_data(self, data, backlog):
        request = string.lower(data['request'])
        print request
        response = {}
        if request == 'login':
            return self.validate_client(data['username'], backlog)
        elif request == 'message':
            self.parse_message(data)
        elif request == 'logout':
            self.validate_logout()
        else:
            # Report invalid request
            pass
        return response


    def createMessageArray(messagetext, username):
        '''
        message[3] = [ TID , username, messagetext ]
        return message
        '''
        pass

    def validate_client(self, username, backlog):
        result = { 'response': 'login', 'username': username }
        global users
        print users
        print username in users
        if username.isalnum() != True:
            # Return error: invalid username
            result['error'] = 'Invalid username!'
            return result
        print 'test3'
        if username in users == True:
            if users[username] == 1:
                # Return error: name already taken
                result['error'] = 'Name already taken!'
            elif users[username] == 0:
                # Return login response, username and messages (from earlier?)
                result['messages'] = backlog
                users[username] = 1
                print 'test1'
        elif username in users == False:
            # Return login response, username (and messages?)
            result['messages'] = backlog
            users[username] = 1
        print 'test2'
        return result
        
    def parse_message(self, data):
        pass

    def validate_logout(self):
        pass
    
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
    backlog = [ { 'user1': 'test message one', 'user2': 'another test message' } ]
    users = { 'user1': 1, 'user2': 0 }

    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
