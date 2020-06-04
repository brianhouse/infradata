#!/usr/bin/env python3

import os
import obspy
import glob
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as spsig
import librosa
from obspy import UTCDateTime

filename = "test.mseed"
# target_freq = 32000
target_freq = 10000


stream = obspy.read(filename)
print(stream)

stream.plot()

trace = stream[0]
data = trace.data
duration = len(data) / trace.stats.sampling_rate
fs = trace.stats.sampling_rate
print("sampling rate (hz)", fs)
print("samples", len(data))
print("duration (s)", duration)

print(data)

# # make time vectors for plotting purposes only
t = np.arange(0, duration, 1. / fs) # in seconds
t_hours = np.arange(0, duration / 3600, 1. / fs / 3600) # in hours

# # 1) force the signal's mean value to be zero
data = data - np.mean(data)

# # 2) limit the signal's amplitude / avoid too large peaks in either direction
data_n = data / np.amax(np.absolute(data))

filename = "%s_%s.wav" % (filename.split('.')[0], target_freq)
path = os.path.join(os.path.dirname(__file__), filename)

multiplier = target_freq / fs
fs_sound = int(fs * multiplier)

print("target_frequency", target_freq)
print("multiplier", multiplier)

librosa.output.write_wav(path, data_n, fs_sound, norm=True)
