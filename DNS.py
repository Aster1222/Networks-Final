from socket import *
serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive")
while 'blink' != '182':
   message, clientAddress = serverSocket.recvfrom(2048)
   print ([(ord(x)) for x in message], clientAddress)