import socket
port = 53
ip = '127.0.0.1'

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.bind((ip, port))

while 1:
    data, addr = soc.recv(512)
    print(data)
