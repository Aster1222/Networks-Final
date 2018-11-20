import numpy as np
from scipy import signal
import scipy.fftpack
from rtlsdr import RtlSdr
import asyncio
import time
from decode import *
import config

def configure_sdr(frequency, offset, sample_rate):
    sdr = RtlSdr()
    center_frequency = frequency - offset # Capture center frequency  
    sdr.sample_rate = sample_rate
    sdr.center_freq = center_frequency
    sdr.gain = 'auto'
    return sdr


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


def smooth(x,window_len=11,window='hanning'):
    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y


def detect_transmitter_on(samples, samp_rate, offset, offset_window=1, fft_window_size=100000, freq_magnitude_threshold=100000):
    fft = scipy.fftpack.fft(samples)
    freqs = scipy.fftpack.fftfreq(len(samples)) * samp_rate
    index = np.where(np.abs(freqs - offset) < offset_window)[0]
    if index.size == 0:
        return False
    index = index[0]

    print('max freq val', np.max(np.abs(fft)[index-fft_window_size:index+fft_window_size]) )
    return (np.max(np.abs(fft)[index-fft_window_size:index+fft_window_size]) 
            > freq_magnitude_threshold)


def detect_transmission_start(wave, amplitude_threshold, count_threshold):
    print(f'count above thresh: {(np.abs(wave[:5000]) > amplitude_threshold).sum()}')
    return (np.abs(wave[:5000]) > amplitude_threshold).sum() > count_threshold

if __name__ == '__main__':
    samp_per_bit = config.rec_samp_rate/config.baud
    sdr = configure_sdr(config.frequency, config.offset, config.rec_samp_rate)
    async def streaming():
        async for samples in sdr.stream(num_samples_or_bytes=config.rec_samp_rate):
            if detect_transmitter_on(samples, config.rec_samp_rate, config.offset):
                wave, new_samp_rate = fm_demodulate(samples, config.frequency, config.offset, config.rec_samp_rate)
                samp_per_bit = new_samp_rate/config.baud
                detected = detect_transmission_start(wave, .5, 1)
                print('detected', detected)
                if detected:
                    smoothed_wave = smooth(np.abs(wave), window_len=21, window='flat')
                    envelope = get_envelope(smoothed_wave)[10:-10]
                    square_wave = binary_slicer(envelope)
                    rec_bits = decode_manchester(square_wave, samp_per_bit)
                    print(f'time: {time.time()}')
                    print(f'received bits: {rec_bits}')
                    print(f'length received bits: {len(rec_bits)}')
                    if len(rec_bits) == 44:
                        col_valid, row_valid = error_correction(rec_bits)
                        demux(rec_bits)
                        np.save(f'samples/{int(time.time())}', samples)
        sdr.close()

    now = time.time()
    epsilon = .001
    while(now - int(now) > epsilon):
        now = time.time()
    print(f'time: {time.time()}')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(streaming())