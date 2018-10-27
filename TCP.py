from socket import *


serverPort = 4000
tcpServerSocket = socket(AF_INET, SOCK_STREAM)
tcpServerSocket.bind(('', serverPort))
hostIP = gethostbyname(gethostname())

tcpServerSocket.listen(1)

print("IP Address: " + str(hostIP))


while 1:
	conn, addr = tcpServerSocket.accept()
	data = conn.recv(1024)
	print("connect with " + str(addr[0]) + " on port" + str(addr[1]))
	print(data.decode())

