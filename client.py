'''
KTN-project 2013 / 2014
'''
import socket


class Client(object):

    #username = ''

    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #login('odd')

    def start(self, host, port):

        self.connection.connect((host, port))
        
        for i in range(7):
            self.send('Hello')
        received_data = self.connection.recv(1024).strip()
        print 'Received from server: ' + received_data
        self.connection.close()

    def message_received(self, message, connection):
        '''
        MessageWorker kaller denne metoden hver gang klient mottar en melding
        Print ut mottat melding, til kommandolinje
        
        '''
        
    def connection_closed(self, connection):
        self.connection.close()

    def send(self, data):
        self.connection.sendall(data)

    def force_disconnect(self):
        self.connection.close()

    def login(username):
        pass

    def logout():
        pass


if __name__ == "__main__":
    client = Client()
    client.start('localhost', 9999)
