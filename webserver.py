import socket
HOST = ''
PORT = 80
BUFFER_SIZE = 1024
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soc.bind((HOST, PORT))
soc.listen(1)
print("Running Webserver " + socket.gethostbyname(socket.gethostname()))
while True:
    connection, addr = soc.accept()
    print("Thanks for connecting to me ", addr)
    cfile = connection.makefile('w')
    cfile.write('HTTP/1.0 200 OK\n\n')
    cfile.write('<html><head><title>Black Site</title></head>')
    cfile.write("<h1>Secret Black Site</h1>")
    cfile.write('<p>Welcome, ' + addr[0] + ":" + str(addr[1]) + '</p>')
    cfile.write('</body></html>')
    cfile.close()

    #httpResponse = """
    """
HTTP/1.1 200 OK
Server: Apache/2.28 (Ubuntu)
Accept-Ranges: bytes
Content-Length: 12
Connection: close
Content-Type: text/html
"""
#    connection.sendall(httpResponse)
