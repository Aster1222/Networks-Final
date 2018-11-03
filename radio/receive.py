
# coding: utf-8

# In[71]:

get_ipython().run_line_magic('pylab', '')
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from rtlsdr import RtlSdr
get_ipython().run_line_magic('matplotlib', 'inline')


# In[72]:

def configure_sdr(frequency, offset, sample_rate):
    sdr = RtlSdr()
    center_frequency = frequency - offset # Capture center frequency  
    sdr.sample_rate = sample_rate
    sdr.center_freq = center_frequency
    sdr.gain = 'auto'
    return sdr


# In[73]:

def collect_samples(sdr, num_samples):
    samples = sdr.read_samples(num_samples)
    sdr.close()  
    del(sdr)
    return samples


# In[74]:

def fm_demodulate(samples, frequency, offset, samp_rate):
    x1 = np.array(samples).astype("complex64")
    # To mix the data down, generate a digital complex exponential 
    # (with the same length as x1) with phase -F_offset/Fs
    fc1 = np.exp(-1.0j*2.0*np.pi* offset/samp_rate*np.arange(len(x1)))  
    # Now, just multiply x1 and the digital complex expontential
    x2 = x1 * fc1  

    # An FM broadcast signal has  a bandwidth of 200 kHz
    f_bw = 200000  
    n_taps = 64  
    # Use Remez algorithm to design filter coefficients
    lpf = signal.remez(n_taps, [0, f_bw, f_bw+(samp_rate/2-f_bw)/4, samp_rate/2], [1,0], Hz=samp_rate)  
    x3 = signal.lfilter(lpf, 1.0, x2)

    dec_rate = int(samp_rate / f_bw)  
    x4 = x3[0::dec_rate]  
    # Calculate the new sampling rate
    new_samp_rate = samp_rate/dec_rate  

    ### Polar discriminator
    y5 = x4[1:] * np.conj(x4[:-1])  
    x5 = np.angle(y5)  

    # The de-emphasis filter
    d = new_samp_rate * 75e-6   # Calculate the # of samples to hit the -3dB point  
    x = np.exp(-1/d)            # Calculate the decay between each sample  
    b = [1-x]                   # Create the filter coefficients  
    a = [1,-x]  
    x6 = signal.lfilter(b,a,x5)  

    # Find a decimation rate to achieve audio sampling rate between 44-48 kHz
    audio_freq = 44100
    dec_audio = int(new_samp_rate/audio_freq)  
    Fs_audio = new_samp_rate / dec_audio

    x7 = signal.decimate(x6, dec_audio)  
    return x7, Fs_audio


# In[75]:

def smooth(x,window_len=11,window='hanning'):
    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y


# In[76]:

def detect_transmission_start(wave, start_threshold):
    for i, s in enumerate(wave):
        if s > start_threshold:
            start = i - 100
            return start


# In[77]:

def get_envelope(wave):
    analytical_signal = signal.hilbert(wave)
    envelope = np.abs(analytical_signal)
    return envelope


# In[78]:

def binary_slicer(envelope):
    avg = np.average(envelope) + .02
    print(f'avg: {avg}')
    sliced = [1 if x > avg else 0 for x in envelope]
    return sliced


# In[79]:

def decode_manchester(square_wave, samp_per_bit, threshold=None):
    if threshold is None:
        threshold = samp_per_bit / 1.5
        
    transitions = []
    for i in range(len(square_wave)-1):
        if square_wave[i] == 1 and square_wave[i+1] == 0:
            transitions.append((i, 0))
        if square_wave[i] == 0 and square_wave[i+1] == 1:
            transitions.append((i, 1))

    valid_transitions = [transitions[0]]
    for t, b in transitions[1:]:
        if np.abs(valid_transitions[-1][0] + (2*samp_per_bit) - t) < threshold:
            valid_transitions.append((t, b))

    bits = [b for _, b in valid_transitions]
    return bits


# In[80]:

frequency = int(88.1e6)  # Pick a radio station  
offset = 250000         # Offset to capture at  
samp_rate = 1140000         # Sample rate  
num_samples = 8192000           # Samples to capture  
baud = 300
samp_per_bit = samp_rate/baud
n_bits = 44


# In[81]:

sdr = configure_sdr(frequency, offset, samp_rate)
samples = collect_samples(sdr, num_samples)
fm_demodulated_wave, new_samp_rate = fm_demodulate(samples, frequency, offset, samp_rate)
plt.plot(fm_demodulated_wave[::10])


# In[82]:

fm_demodulated_wave_1 = fm_demodulated_wave[1000:]
start_threshold = .25
start = detect_transmission_start(fm_demodulated_wave_1, start_threshold)
start -= 100
samp_per_bit = new_samp_rate/baud
stop = start + int(2 * samp_per_bit * n_bits)
fm_demodulated_wave_2 = fm_demodulated_wave_1[start:stop]
smoothed_wave = smooth(np.abs(fm_demodulated_wave_2), window_len=21, window='flat')
plt.plot(smoothed_wave[::10])


# In[83]:

envelope = get_envelope(smoothed_wave)[10:-10]
square_wave = binary_slicer(envelope)
plt.plot(envelope)
plt.plot(square_wave)


# In[84]:

rec_bits = decode_manchester(square_wave, samp_per_bit)
print(rec_bits)
print(len(rec_bits))


# In[85]:

sent_bits = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0])


# In[86]:

for i, rec_sent in enumerate(list(zip(rec_bits, sent_bits))):
    if rec_sent[0] != rec_sent[1]:
        print(i)


# In[87]:

def error_correction(rec_bits):
    grid = np.array(rec_bits[:-12]).reshape(4,8)
    col_parity = grid.sum(axis=0) % 2
    row_parity = grid.sum(axis=1) % 2
    received_col_parity = np.array(rec_bits[32:40])
    received_row_parity = np.array(rec_bits[40:44])
    col_valid = np.array_equal(col_parity, received_col_parity)
    row_valid = np.array_equal(row_parity, received_row_parity)
    return col_valid, row_valid


# In[88]:

print(error_correction(rec_bits))


# In[89]:

def demux(packet):
    char_binary = ''.join(str(b) for b in packet[24:32])
    print(char_binary)
    print(chr(int(char_binary, 2) ^ 170))

demux(rec_bits)
    


# In[ ]:



