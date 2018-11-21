#!/usr/bin/env python3

from socket import *
from radio import transmit, config
import time


if __name__ == '__main__':
    serverPort = 4000
    tcpServerSocket = socket(AF_INET, SOCK_STREAM)
    tcpServerSocket.bind(('', serverPort))
    hostIP = gethostbyname(gethostname())

    tcpServerSocket.listen(1)

    print("IP Address: " + str(hostIP))

    conn, addr = tcpServerSocket.accept()
    print("connect with " + str(addr[0]) + " on port" + str(addr[1]))

    while True:
        data = conn.recv(1024)
        if (data.decode().lower().strip() == "exit"):
            conn.close()
            break
        
        message = data.decode()
        print(f'Transmitting the following message')
        print(message)
        bits = ''
        for c in message.strip():
            xor_bitstring = str(bin(ord(c) ^ ord(config.otp[config.otp_pos])))[2:]
            for _ in range(8 - len(xor_bitstring)):
                xor_bitstring = '0' + xor_bitstring

            bits += xor_bitstring
            config.otp_pos = (config.otp_pos + 1) % config.otp_len

        print(bits)

        transmit.transmit(bits)
