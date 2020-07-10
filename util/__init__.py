import time
import subprocess
import cairo
import gzip
import pickle
import numpy as np
# from .log_config import log, config


def drawing(width, height):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.rectangle(0, 0, width, height)
    ctx.set_source_rgba(255, 255, 255)
    ctx.fill()
    return surface, ctx

def output(surface):
    filename = f"charts/{int(time.time())}.png"
    surface.write_to_png(filename)
    subprocess.call(["open", filename])

def save(data):
    with gzip.open("spectrum.pklz", 'wb') as f:
        f.write(pickle.dumps(data))

def load():
    with gzip.open("spectrum.pklz") as f:
        data = pickle.loads(f.read())
    return data

def normalize(signal, minimum=None, maximum=None):
    if minimum is None:
        minimum = np.min(signal)
    if maximum is None:
        maximum = np.max(signal)
    signal -= minimum
    maximum -= minimum
    signal /= maximum
    return signal
