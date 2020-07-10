#!/usr/bin/env python3

print("Loading modules...")

import os
import math
import datetime
import json
import numpy as np
import matplotlib.pyplot as plt
import librosa
import cairo
import colorsys
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import URL_MAPPINGS, FDSNNoDataException
from obspy import UTCDateTime
from util import *


NETWORK, STATION = "UO", "RAIN"
CHANNEL = "BDF"
FREQUENCY_MULTIPLIER = 100
WINDOW_SIZE = 256 # 512


## get data
client = Client("IRIS")
current_t = datetime.datetime.utcnow()
start_t = (input("Start [%s]: " % (current_t - datetime.timedelta(hours=1))) or current_t - datetime.timedelta(hours=1))
stop_t  = (input("Stop  [%s]: " % current_t) or current_t)
start_t = UTCDateTime(str(start_t))
stop_t  = UTCDateTime(str(stop_t))
print()
print("Retrieving data...")
try:
    stream = client.get_waveforms(NETWORK, STATION, "*", CHANNEL, start_t, stop_t)
except FDSNNoDataException as e:
    print(e)
    exit()
trace = stream[0]
print(trace.stats)
save(trace)
trace = load()


## convert to audio signal
print()
print("Converting to audio...")
signal = trace.data - np.mean(trace.data)
signal /= np.amax(np.absolute(signal))
fs = trace.stats.sampling_rate
filename = f"output.wav"
path = os.path.join(os.path.dirname(__file__), "wav", filename)
librosa.output.write_wav(path, signal, int(fs * FREQUENCY_MULTIPLIER), norm=True)
print(f"--> saved {filename}")
print()
print("Analyzing as audio...")
spectrum, freqs, ts, image = plt.specgram(signal, NFFT=WINDOW_SIZE, Fs=fs, noverlap=WINDOW_SIZE / 2, mode="psd", scale="dB")
spectrum = np.abs(spectrum)             # convert to amplitude / magnitude
spectrum = np.log10(spectrum)           # convert to logarithmic dB scale
spectrum = normalize(spectrum)          # normalize
print(f"--> time columns {len(ts)}")
print(f"--> freq rows {len(freqs)}")

spectrum = sigmoid(spectrum, 1)

## draw
print()
print(f"Drawing...")
X_MULT = 1
Y_MULT = 1
OVERLAP = 0
surface, ctx = drawing(len(ts) * X_MULT, len(freqs) * Y_MULT)
ctx.set_line_width(1)
for f in range(len(freqs)):
    for t in range(len(ts)):
        v = spectrum[f][t]
        # color = v, 1.0, v
        # color = colorsys.hsv_to_rgb(*color[:3])
        color = [1-v] * 3 # bw
        ctx.set_source_rgba(color[0], color[1], color[2], 1 / (OVERLAP + 1))
        x, y = t * X_MULT, (len(freqs) - f - 1) * Y_MULT
        ctx.rectangle(x - OVERLAP, y - OVERLAP, X_MULT + OVERLAP*2, Y_MULT + OVERLAP*2)
        ctx.fill()

output(surface)

# colormap = plt.get_cmap('cividis')
# plt.imshow(colormap(np.flipud(spectrum)))
# plt.show()
