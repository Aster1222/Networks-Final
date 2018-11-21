#!/usr/bin/env python3
import numpy as np
from scipy import signal
import config

def get_envelope(wave):
    analytical_signal = signal.hilbert(wave)
    envelope = np.abs(analytical_signal)
    return envelope

def binary_slicer(envelope):
    avg = np.average(envelope) + .02
    sliced = [1 if x > avg else 0 for x in envelope]
    return sliced

def decode_manchester(square_wave, samp_per_bit, threshold=None):
    if threshold is None:
        threshold = samp_per_bit / 1.5
        
    transitions = []
    for i in range(len(square_wave)-1):
        if square_wave[i] == 1 and square_wave[i+1] == 0:
            transitions.append((i, 0))
        if square_wave[i] == 0 and square_wave[i+1] == 1:
            transitions.append((i, 1))

    if not transitions:
        return []
    valid_transitions = [transitions[0]]
    for t, b in transitions[1:]:
        if np.abs(valid_transitions[-1][0] + (2*samp_per_bit) - t) < threshold:
            valid_transitions.append((t, b))

    bits = [b for _, b in valid_transitions]
    return bits

def checksum(packet):
    return (sum(packet[:2] + packet[3:]) % 2) == packet[2]

def bits2ascii(b):
    return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(b)]*8))

def demux(packet):
    if not (len(packet) >= 3 and checksum(packet) and packet[0] == config.cur_id):
        return False, None, None

    valid = True
    config.cur_id = (config.cur_id + 1) % 2
    fragmented = (packet[2] == 1)
    bitstring = ''.join(str(b) for b in packet[3:])
    ascii_str = bits2ascii(bitstring)
    for c in ascii_str:
        message += str(chr(ord(c) ^ ord(one_time_pad[config.otp_pos])))
        config.otp_pos = (config.otp_pos + 1) % config.otp_len
    return valid, message, fragmented
