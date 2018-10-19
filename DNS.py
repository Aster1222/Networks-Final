# import socket
# port = 53
# ip = '127.0.0.1'
#
#
# def getIP(domainName):
#     if domainName.decode() == 'blacksite.secret':
#         return b'192.168.56.1'
#     else:
#         return socket.gethostbyname(domainName)
#
#
# soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# soc.bind((ip, port))
# soc.listen(5)  # #
# while 1:
#     client, addr = soc.accept()
#     data = client.recv(1024)
#     if data:
#         client.send(getIP(data))
#     client.close()

from socket import *
serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive")
while 'blink' != '182':
   message, clientAddress = serverSocket.recvfrom(2048)
   print (message)