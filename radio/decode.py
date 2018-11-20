import numpy as np
from scipy import signal

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

def error_correction(rec_bits):
    grid = np.array(rec_bits[:-12]).reshape(4,8)
    col_parity = grid.sum(axis=0) % 2
    row_parity = grid.sum(axis=1) % 2
    received_col_parity = np.array(rec_bits[32:40])
    received_row_parity = np.array(rec_bits[40:44])
    col_valid = np.array_equal(col_parity, received_col_parity)
    row_valid = np.array_equal(row_parity, received_row_parity)
    return col_valid, row_valid

def demux(packet):
    char_binary = ''.join(str(b) for b in packet[24:32])
    print(char_binary)
    print(chr(int(char_binary, 2) ^ 170))


if __name__ == '__main__':
    file_name = sys.argv[1]
    fm_demodulated_wave = np.load(file_name)

    smoothed_wave = smooth(np.abs(fm_demodulated_wave_2), window_len=21, window='flat')

    envelope = get_envelope(smoothed_wave)[10:-10]
    square_wave = binary_slicer(envelope)

    rec_bits = decode_manchester(square_wave, samp_per_bit)
    print(rec_bits)
    print(len(rec_bits))

    print(error_correction(rec_bits))

    demux(rec_bits)

