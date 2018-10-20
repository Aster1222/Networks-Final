from socket import *

'''
RFC: https://www.ietf.org/rfc/rfc1035.txt
'''

def responsePacketBuilder(message):
	#### This grabs the transaction id from the UDP packet ####
	transaction_id = ''
	for i in message[:2]:
		transaction_id += hex(i)[2:]

	print(transaction_id)

	#### This gets the flags ####

	QR = '1'
	OPCODE = ''

	byte1 = bytes(message[2:3])
	byte2 = bytes(message[3:4])


	for i in range(1, 5):
		OPCODE += str(ord(byte1)&(1 << i))

	AA = '1' # always 1, basically says that we are the authority
	TC = '0' # assuming never truncated but this may change
	RD = '0' # we are probably not going to support recursion
	RA = '0' # we are not going to say recursion is available
	Z = '000' # no use for these future use bytes
	responseCode = '0000' # we are not going to send any other type of response codes

	flags =  int(QR+OPCODE+AA+TC+RD, 2).to_bytes(1, byteorder='big') + int(RA + Z + responseCode, 2).to_bytes(1, byteorder='big')
	print(flags)


	#### This sets the question count ####

serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive")

while 'blink' != '182':
   message, clientAddress = serverSocket.recvfrom(2048)
   repsonse = responsePacketBuilder(message)
   # serverSocket.sendto(response, clientAddress)




