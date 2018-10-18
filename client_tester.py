import socket
dnsIP = '127.0.0.1'
dnsPort = 53
query = b'blacksite.secret'
size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((dnsIP, dnsPort))
s.send(query)
data = s.recv(size)
print(data)
