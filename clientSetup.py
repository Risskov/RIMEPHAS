import socket

#HOST = "10.126.94.117"
HOST = "10.126.128.26"

class Client():
    def __init__(self, address=(HOST, 5000)):
        self.socket = socket.socket()
        self.socket.connect(address)
    
    def send(self, data):
        self.socket.sendall(bytes(str(data), 'utf8'))
        #self.socket.sendall(b"data")

    def close(self):
        self.socket.close()

if __name__ == '__main__':
    client = Client()
    client.send(2219)
    client.close()
