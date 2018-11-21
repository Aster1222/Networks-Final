transmit_samp_rate = 44100
baud = 300
len_preamble = 8
frequency = int(88.1e6)
offset = 250000
rec_samp_rate = 2**21
cur_id = 0
save_samples = False
otp_pos = 0
otp = """11111111111111111111111111
000000000000000000000000000000000000000000000000000000000
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
tjgbhjbklvgjcfjvuhvdcugp9-32098r62 07<F2>=9<F2>8=09q7rt-934u assda;kjbcvfp98YR023   
FQPEW8650R924QFGHW09F7GT0WQ7T40287TRWEBLIWpio7t3r0p3OTG*^R(**Y&^*)(&%*)("""
otp_len = len(otp)
