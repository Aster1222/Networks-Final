from socket import *


serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))


'''
RFC: https://www.ietf.org/rfc/rfc1035.txt
following this for variable naming conventions
'''

def flagger(message):
	QR = '1'
	OPCODE = ''
	byte1 = bytes(message[:1])

	for i in range(1, 5):
		OPCODE += str(ord(byte1)&(1 << i))

	AA = '1' # always 1, basically says that we are the authority
	TC = '0' # assuming never truncated but this may change
	RD = '0' # we are probably not going to support recursion
	RA = '0' # we are not going to say recursion is available
	Z = '000' # no use for these future use bytes
	RCODE = '0000' # we are not going to send any other type of response codes

	return int(QR+OPCODE+AA+TC+RD, 2).to_bytes(1, byteorder='big') + int(RA+Z+RCODE, 2).to_bytes(1, byteorder='big')

def getQuestionDomain(message):
	recordingPath = 0
	expectedLength = 0
	domainString = ''
	domainParts = []
	lengthRecordedOnThisPart = 0

	for byte in message:
		if recordingPath:
			if byte != 0:
				domainString += chr(byte)
			lengthRecordedOnThisPart += 1
			if lengthRecordedOnThisPart == expectedLength:
				domainParts.append(domainString)
				domainString = ''
				recordingPath = 0
				lengthRecordedOnThisPart = 0
			if byte == 0:
				domainParts.append(domainString)
				break
		else:
			recordingPath = 1
			expectedLength = byte

	return domainParts

def buildquestion(domainname):
	qbytes = b''

	for part in domainname:
		qbytes += bytes([len(part)])
		for char in part:
			qbytes += ord(char).to_bytes(1, byteorder="big")

	return qbytes + (1).to_bytes(2, byteorder="big") + (1).to_bytes(2, byteorder="big")

def getDNSBody(recttl, recval):

    rbytes = b'\xc0\x0c' + bytes([0]) + bytes([1]) + bytes([0]) + bytes([1]) + int(recttl).to_bytes(4, byteorder='big') + bytes([0]) + bytes([4])

    for part in recval.split('.'):
    	rbytes += bytes([int(part)])

    return rbytes


def responsePacketBuilder(message):
	#### This grabs the transaction id from the UDP packet ####
	transaction_id = message[:2]

	#### This gets the flags ####

	flags = flagger(message[2:])

	#### This sets the question count ####

	QDCOUNT = b'\x00\x01' # this assumes only one question

	#### ANSWER COUNT ####
	ANCOUNT = (1).to_bytes(2, byteorder="big") # thus only one answer

	#### NAME SERVER COUNT ####
	NSCOUNT = (0).to_bytes(2, byteorder="big") # we are assuming that there is no nameservers to make things easier

	#### ADDITIONAL COUNT ####
	ARCOUNT = (0).to_bytes(2, byteorder="big") # we are assuming there is no additional stuff to make things easier

	dnsheader = transaction_id + flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

	domainname = getQuestionDomain(message[12:])
	dnsquestion = buildquestion(domainname)

	dnsbody = getDNSBody(400, "192.168.0.21")

	return dnsheader + dnsquestion + dnsbody


print("The server is ready to receive", gethostbyname(gethostname()))

while 1:
   message, clientAddress = serverSocket.recvfrom(2048)
   response = responsePacketBuilder(message)
   serverSocket.sendto(response, clientAddress)




