#!/usr/bin/env python3

from socket import *
from radio import transmit
import time

serverPort = 4000
tcpServerSocket = socket(AF_INET, SOCK_STREAM)
tcpServerSocket.bind(('', serverPort))
hostIP = gethostbyname(gethostname())


def one_time_pad(og_message, key):
    return og_message ^ key


tcpServerSocket.listen(1)

print("IP Address: " + str(hostIP))

conn, addr = tcpServerSocket.accept()
print("connect with " + str(addr[0]) + " on port" + str(addr[1]))

while True:
    data = conn.recv(1024)
    original_data = ord(data.decode()[0])
    print("binary of single letter transmitted it: " +
          "0" + str(bin(original_data))[2:])
    encoded = str(bin(original_data ^ 170))[2:]
    print("binary of one time pad:               :", bin(170)[2:])
    print("binary of result                      :", encoded + '\n')

    for _ in range(10):    
        print(f'time: {time.time()}')
        transmit.transmit(encoded)

    if (data.decode().lower().strip() == "exit"):
        conn.close()
        break


'''
Packet Structure

Pre-Amble: 11111111
Header:
	ID: 00000000
	Length: 00000000
Body:
	Data: 0000000
Error Detection:
	Bit Parity: 000000000000

10101010
00000000
00000000
00000000

'''
