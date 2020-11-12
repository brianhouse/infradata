#!/usr/bin/env python3

print("Loading modules...")

import os, sys
import math
import datetime
import json
import numpy as np
import matplotlib.pyplot as plt
import librosa
import cairo
import colorsys
from skimage import io, filters, morphology, restoration
from util import *

WINDOW_SIZE = 400 # 256

if len(sys.argv) < 2:
    print("[path.wav]")
    exit()
filepath = sys.argv[1]
filename = os.path.basename(filepath)


sr = int(filepath.split("_")[-1].split(".")[0])
signal, sr = librosa.load(filepath, sr=sr)

print()
print("Analyzing as audio...")
spectrum, freqs, ts, image = plt.specgram(signal, NFFT=WINDOW_SIZE, Fs=sr, noverlap=WINDOW_SIZE / 2, mode="psd", scale="dB")
spectrum = np.abs(spectrum)             # convert to amplitude / magnitude
spectrum = np.log10(spectrum)           # convert to logarithmic dB scale
spectrum = normalize(spectrum)          # normalize
print(f"--> time columns {len(ts)}")
print(f"--> freq rows {len(freqs)}")

###


spectrum **= 2.8    # compress high values a bit (gamma function)

## I feel like there is a lot of subtle detail since it's pixel by pixel, and that the morphology is too coarse

# spectrum = restoration.denoise_tv_chambolle(spectrum, weight=0.0125)


# spectrum_mask = spectrum > .3
# spectrum_mask = morphology.closing(spectrum_mask)
# spectrum = spectrum * spectrum_mask




###

colormap = plt.get_cmap('binary')
# colormap = plt.get_cmap('cividis')
spectrum = colormap(spectrum)

# custom draw
print()
print(f"Drawing...")
X_MULT = 1
Y_MULT = 1
OVERLAP = 0
TRIM = 2
surface, ctx = drawing(len(ts) * X_MULT, (len(freqs) - TRIM) * Y_MULT)
ctx.set_line_width(1)
for f in range(TRIM,len(freqs)):
    for t in range(len(ts)):
        color = spectrum[f][t]
        ctx.set_source_rgba(color[0], color[1], color[2], 1 / (OVERLAP + 1))
        x, y = t * X_MULT, (len(freqs) - f - 1) * Y_MULT
        ctx.rectangle(x - OVERLAP, y - OVERLAP, X_MULT + OVERLAP*2, Y_MULT + OVERLAP*2)
        ctx.fill()

prefix = os.path.splitext(filename)[0] + "_" + str(int(time.time()))
output(surface, prefix)

## draw with io
# io.imshow(np.flipud(spectrum))
# io.show()
