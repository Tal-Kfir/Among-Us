import socket
import config

class clientnetwork():
    def __init__(self):
        self.sock = socket.socket()
        self.sock.settimeout(0.1)
    
    
    def connect(self):
        try:
            self.sock.connect((config.SERVER_IP,config.SERVER_PORT))
            return True
        except Exception as e:
            return False
    
    def close(self):
        try:
            self.sock.close()
        except Exception as e:
            pass
    
    def send_data(self, data):
        try:
            self.sock.send(data)
            return True
        except Exception as e:
            return False


    def get_data(self):
        try:
            data = self.sock.recv(1024)
            if (not data is None) and (not data == b""):
                return (True, data)
            else:
                return (False, b'')
        except Exception as e:
            return (False, b'')