'''
KTN-project 2013 / 2014
Python daemon thread class for listening for events on
a socket and notifying a listener of new messages or
if the connection breaks.

A python thread object is started by calling the start()
method on the class. in order to make the thread do any
useful work, you have to override the run() method from
the Thread superclass. NB! DO NOT call the run() method
directly, this will cause the thread to block and suspend the
entire calling process' stack until the run() is finished.
it is the start() method that is responsible for actually
executing the run() method in a new thread.
'''
from threading import Thread
import client


class ReceiveMessageWorker(Thread):

    def __init__(self, listener, connection):
        self.daemeon = True
        connectionSevered = False
        connection.settimeout(3.0)
        print listener

    def run(self):
        while connectionSevered == False:
            try:
                connection.listen(1)
                Client.message_received(connection)
            except socket.error as msg:
                Client.connection_closed(connection)
