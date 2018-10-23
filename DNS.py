from socket import *


serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))


"""
RFC: https://www.ietf.org/rfc/rfc1035.txt
following this for variable naming conventions
"""

def flagger(message):
	"""
	This method takes in all parts of the message after the transaction id to get the flags. Really only uses 1 byte.
	Normally we would do some  bitwise calculation to calculate all the flags, but since we are always responding with the same
	DNS response, we don't need to do those calculations
	:param message: every part of the message after the transcation ID
	:return: returns a byte string containing all the flags
	"""
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
	"""
	This method basically takes in part of the message (everything after the header) and spits out the URL
	Normally, we'd calculate the qt value too, but since this DNS always spits back the same IP, we can hard code that too
	:param message: everything in the message post header
	:return: parts of the domain
	"""
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
	"""
	This builds the dns question. Basically, it conerts the domain name into a byte string and pads the end with a couple of bytes
	:param domainname: this is a list of two strings that contains the parts of the name
	:return: returns the final question byte string
	"""
	questionBytes = b''

	for part in domainname:
		questionBytes += bytes([len(part)])
		for char in part:
			questionBytes += ord(char).to_bytes(1, byteorder="big")

	return questionBytes + (1).to_bytes(2, byteorder="big") + (1).to_bytes(2, byteorder="big")

def getDNSBody(targetIPAddress):
	"""
	This builds up the DNS body. Most the of the values are hard coded and the only dynamically generated value is the IP
	:param targetIPAddress: this is the IP address of the target webserver that the DNS server is trying to return (in this case it is the same IP address as the DNS server)
	:return: the final DNS body
	"""
	NAME = b'\xc0\x0c'
	TYPE = bytes([0]) + bytes([1])
	CLASS = bytes([0]) + bytes([1])
	TTL = int(420).to_bytes(4, byteorder='big')
	RDLENGTH = bytes([0]) + bytes([4])
	RDDATA = b''

	for part in targetIPAddress.split('.'):
		RDDATA += bytes([int(part)])

	return NAME + TYPE + CLASS + TTL + RDLENGTH + RDDATA


def responsePacketBuilder(message):
	"""
	This builds the response packet based on the message recieved by the server.
	Note: the packet is mostly static with a couple dynamic parts as needed
	:param message: the original message recieved by the server
	:return: the fully build and ready to be sent response packet
	"""
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

	#### Finish building the head ####
	dnsheader = transaction_id + flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

	domainname = getQuestionDomain(message[12:])
	dnsquestion = buildquestion(domainname)

	dnsbody = getDNSBody(gethostbyname(gethostname()))

	return dnsheader + dnsquestion + dnsbody


print("The server is ready to receive:", gethostbyname(gethostname()))

while 1:
   message, clientAddress = serverSocket.recvfrom(2048)
   response = responsePacketBuilder(message)
   serverSocket.sendto(response, clientAddress)









