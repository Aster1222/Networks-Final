from socket import *
# import soundcard
# import numpy

# import pyaudio

serverPort = 4000
tcpServerSocket = socket(AF_INET, SOCK_STREAM)
tcpServerSocket.bind(('', serverPort))
hostIP = gethostbyname(gethostname())

tcpServerSocket.listen(1)

print("IP Address: " + str(hostIP))

conn, addr = tcpServerSocket.accept()
print("connect with " + str(addr[0]) + " on port" + str(addr[1]))

while 1:
	data = conn.recv(1024)
	print("binary of single letter transmitted it: " + str(bin(ord(data.decode()[0])))[2:])

	if (data.decode().lower().strip() == "exit"):
		conn.close()
		break




