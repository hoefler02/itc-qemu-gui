from PySide2 import QtCore
import threading
import socket
import json
import time

class QMP(threading.Thread, QtCore.QObject):

    stateChanged = QtCore.Signal(str)
    emptyReturn = QtCore.Signal(bool)
    memoryMap = QtCore.Signal(list)

    def __init__(self, host, port):

        QtCore.QObject.__init__(self)
        threading.Thread.__init__(self)
        
        # Kill thread when parent dies
        self.daemon = True 

        # Socket creation
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.responses = []

        # QMP setup
        self.qmp_command('qmp_capabilities')
        self.listen() # pluck empty return object
        self.qmp_command('query-status')
        self._running = None
        self._empty_return = None

    def run(self):
        while True:
            data = self.listen()
            if data == 'lost_conn':
                self.running = 'error'
                break
            # Handle Async QMP Messages 
            if 'timestamp' in data:
                if data['event'] == 'STOP':
                    self.running = 'paused'
                elif data['event'] == 'RESUME': 
                    self.running = 'running'
            # Handle Status Return Messages
            elif 'return' in data and 'running' in data['return']:
                if data['return']['running']:
                    self.running = 'running'
                else:
                    self.running = 'paused'
            elif 'return' in data and len(data['return']) == 0:
                self.empty_return = True
            elif 'return' in data and 'memorymap' in data['return']:
                self.memorymap = data['return']

    def listen(self):
        
        total_data = bytearray() # handles large returns
        while True:
            data = self.sock.recv(1024)
            if not data:
                return 'lost_conn'
            total_data.extend(data)
            if len(data) < 1024:
                break

        data = total_data.decode().split('\n')[0]
        data = json.loads(data)
        self.responses.append(data)
        return data

    def qmp_command(self, cmd):
        qmpcmd = json.dumps({'execute': cmd})
        self.sock.sendall(qmpcmd.encode())

    def hmp_command(self, cmd):
        hmpcmd = json.dumps({'execute': 'human-monitor-command', 'arguments': {'command-line': cmd}})
        self.sock.sendall(hmpcmd.encode())
        time.sleep(0.1) # wait for listen to capture data and place it in responses dictionary
        return self.responses[-1]
    
    @property
    def running(self):
        return self._running
    
    @running.setter
    def running(self, value):
        # print('sent: ', value)
        self._running = value
        self.stateChanged.emit(value)