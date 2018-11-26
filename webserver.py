# !/usr/bin/env python
import socket

TCP_IP = ''
TCP_PORT = 80
BUFFER_SIZE = 1020

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Running Webserver on " + socket.gethostbyname(socket.gethostname()))

while True:
    conn, addr = s.accept()
    print("Thanks for connecting:", addr)
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    print("received data:", data)
    httpResponse = """HTTP/1.1 200 OK
    Server: Apache/2.2.8 (Ubuntu)
    Accept-Ranges: bytes
    Content-Length: 12
    Connection: close
    Content-Type: text/html

    <HTML><body style="background-color: black"> <h1 style="color: white" >Super Secret Blacksite</h1><p style="color: white"> Requester IP: """ + str(addr[0]) + """</p></body></HTML>"""

    print(httpResponse)
    conn.send(httpResponse.encode())  # send response
    conn.close()
