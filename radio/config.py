#/usr/bin/env python3

path = '/Users/collinshuff/Documents/UVa-Fall18/CS4457/Networks-Final/radio/samples'
save_samples = True
debug = False

# Transmission/Reception Parameters
transmit_samp_rate = 44100
rec_samp_rate = 2**21
baud = 300
frequency = int(88.1e6)
offset = 150000
repeat_transmission = 1

# Packet parameters
len_preamble = 5
cur_id = 0
packet_id_pos = len_preamble
packet_fragment_pos = len_preamble + 1
packet_checksum_pos = len_preamble + 2
packet_header_len = len_preamble + 3

# One Time Pad
otp_pos = 0
otp = 'The quick brown fox jumped over the lazy dog'
otp_len = len(otp)
