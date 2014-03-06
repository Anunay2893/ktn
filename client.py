'''
KTN-project 2013 / 2014
'''
from workers import *
import socket
import json

class Client(object):

    username = 'user2'

    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        self.connection.connect((host, port))
        
    
    def parse_server_data(self):
        while True:
            data_json = self.connection.recv(1024)
            if not data_json:
                return
            else:
                try:
                    data = json.loads(data_json)
                    print data
                    print '\n'
                except:
                    pass
    
    
    '''    
    def parse_server_data(self):
        data_json = self.connection.recv(1024)
        if not data_json:
            return
        else:
            try:
                data = json.loads(data_json)
                print data
            except:
                pass
    '''
        
    def close_connection(self, connection):
        print 'Connection closed'
        self.connection.close()

    def send(self, data):
        self.connection.sendall(json.dumps(data))
        #print data

    def force_disconnect(self):
        self.connection.close()

    def login(self):
        data = { 'request': 'login', 'username': self.username }
        self.send(data)
        print data

    def logout(self):
        data = { 'request': 'logout' }
        self.send(data)

    def handle_input(self):
        userInput = raw_input('Enter message: ');
        data = { 'request': 'message', 'message': userInput }
        return data


if __name__ == "__main__":
    client = Client()
    client.start('localhost', 9997)
    # Thread for handling and parsing received data
    receiver = ReceiveMessageWorker(client)
    receiver.start()
    # Thread for taking input and sending data
    sender = SendMessageWorker(client)
    sender.start()
