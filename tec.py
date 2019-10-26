#!/usr/bin/env python3

import serial
import time
import numpy as np
from obspy import UTCDateTime, read, Trace, Stream

PORT = '/dev/tty.usbserial'

"""
 Each output sample is an ASCII record terminated by LF and CR. The samples range from -32767 to +32767.
 50hz sample rate
 built in low-pass filter at 20hz
 0.05–20hz

"""

data = []
t_previous = 0
t_start = None

with serial.Serial(PORT, 9600, timeout=1) as device:
    while True:
        line = None
        try:
            t = time.time()
            elapsed = t - t_previous
            t_previous = t
            line = device.readline()
            line = line.strip().decode('ascii')
            value = int(line[1:]) * (-1 if line[0] == '-' else 1)
            # datum = time.time(), value
            datum = value
            print(datum)
            data.append(datum)
            if t_start is None:
                t_start = t
        except (ValueError, UnicodeDecodeError) as e:
            print(e, line)
        except KeyboardInterrupt as e:
            break

data = np.array(data, dtype='int16')

stats = {   'network': 'BH', 
            'station': 'FLDS', 
            'location': '',
            'channel': 'BDF', 
            'sampling_rate': 50.0,
            'npts': len(data)
            }

stats['starttime'] = t_start
stream = Stream([Trace(data=data, header=stats)])
stream.write("test.mseed", format='MSEED')#, encoding=0)#, reclen=256)            

"""
how should this work? to a database, no?

"""