import bluetooth

# 00001101-0000-1000-8000-00805F9B34FB

class BoseBT:
    def __init__(self, address):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((address, 8))

    def send(self, data):
        return self.sock.send(bytes(data))

    def recv(self):
        return self.sock.recv(1024)
