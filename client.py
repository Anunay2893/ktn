'''
KTN-project 2013 / 2014
'''
import socket
import MessageWorker
import json

class Client(object):

    username = 'student'

    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        self.connection.connect((host, port))
        #worker = MessageWorker.ReceiveMessageWorker(self, self.connection)
        #self.login(self.username)
        data = self.read_input()
        print data
        self.send(data)
        self.message_received(self.connection)
        

    def message_received(self, connection):
        '''
        MessageWorker kaller denne metoden hver gang klient mottar en melding
        Print ut mottatt melding, til kommandolinje
        
        '''
        received_data = json.loads(self.connection.recv(1024).strip())
        print received_data
        
    def connection_closed(self, connection):
        self.connection.close()

    def send(self, data):
        self.connection.sendall(json.dumps(data))

    def force_disconnect(self):
        self.connection.close()

    def login(self, username):
        data = [ { 'request': 'login', 'username': username } ]
        self.send(data)

    def logout():
        data = [ { 'request': 'logout' } ]
        self.send(data)

    def read_input(self):
        userInput = raw_input('Enter message: ');
        data = [ { 'request': 'message', 'message': userInput } ]
        return data


if __name__ == "__main__":
    client = Client()
    client.start('localhost', 9999)
