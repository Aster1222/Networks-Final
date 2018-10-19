# import socket
# HOST = '199.111.227.46'
# PORT = 80
# BUFFER_SIZE = 1024
# soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# soc.bind((HOST, PORT))
# soc.listen(1)
# print("Running Webserver " + socket.gethostbyname(socket.gethostname()))
#
# #dnsSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #dnsHost = "192.168.56.1"
# #dnsPort = 53
# #dnsSocket.connect((dnsHost, dnsPort))
#
# while True:
#     connection, addr = soc.accept()
#     print("Thanks for connecting to me ", addr)
#
#     cfile = connection.makefile('w')  # This is what displays on the page
#     cfile.write('HTTP/1.0 200 OK\n\n')
#     cfile.write('<html><head><title>Black Site</title></head>')
#     cfile.write("<h1>Secret Black Site</h1>")
#     cfile.write('<p>Welcome, ' + addr[0] + ":" + str(addr[1]) + '</p>')
#     cfile.write('</body></html>')
#     cfile.close()
#
#     # Not sure if we need this / what its for, but he had it in his demo
#     #httpResponse = """
#     """
# HTTP/1.1 200 OK
# Server: Apache/2.28 (Ubuntu)
# Accept-Ranges: bytes
# Content-Length: 12
# Connection: close
# Content-Type: text/html
# """
#

# !/usr/bin/env python
import socket

TCP_IP = ''
TCP_PORT = 80
BUFFER_SIZE = 1020

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Running Webserver on " + socket.gethostbyname(socket.gethostname()))

while 1:
	conn, addr = s.accept()
	print("Thanks for connecting:", addr)
	data = conn.recv(BUFFER_SIZE)
	if not data: break
	print("received data:", data)
	httpResponse = """HTTP/1.1 200 OK
    Server: Apache/2.2.8 (Ubuntu)
    Accept-Ranges: bytes
    Content-Length: 12
    Connection: close
    Content-Type: text/html

    Hello world!"""

	print(httpResponse)
	conn.send(httpResponse.encode())  # send response
	conn.close()
