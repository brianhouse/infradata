#!/usr/bin/env python3

print("Loading modules...")

import os
import datetime
import subprocess
import obspy
import json
import numpy as np
import librosa
from pprint import pprint
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import URL_MAPPINGS, FDSNNoDataException
from obspy import UTCDateTime

client = Client("IRIS")
channel = (input("Channel [BDF]: ") or "BDF").upper().strip()

current_t = datetime.datetime.utcnow()
start_t = (input("Start [%s]: " % (current_t - datetime.timedelta(days=1))) or current_t - datetime.timedelta(days=1))
stop_t  = (input("Stop  [%s]: " % current_t) or current_t)
start_t = UTCDateTime(str(start_t))
stop_t  = UTCDateTime(str(stop_t))
print()

print("Found stations:")
inventory = client.get_stations(channel=channel, starttime=start_t, endtime=stop_t)
# inventory.plot()
stations = inventory.get_contents()['stations']
for s, station in enumerate(stations):
    print("%d:" % s, station)

while True:
    while True:
        station_index = int(input("Station index: "))

        network, station = stations[station_index].split('.')
        station = station.split(' ')[0]

        print("Retrieving data from %s.%s..." % (network, station))
        try:
            stream = client.get_waveforms(network, station, "*", channel, start_t, stop_t)
        except FDSNNoDataException as e:
            print(e)
            break

        ## save after selecting a given trace?
        filename = ("%s.%s-%s_%s.mseed" % (network, station, channel, str(start_t).split('T')[0]))
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", filename))
        stream.write(path, format="MSEED")
        try:
            stream.plot()
        except Exception as e:
            print(e)

        print()
        print(stream)
        trace = stream[0]
        print()
        print("Using trace 0:")
        print(trace.stats)
        channel = trace.stats.channel
        print()
        data = trace.data
        duration = len(data) / trace.stats.sampling_rate
        fs = trace.stats.sampling_rate
        print("Sampling rate (hz):", fs)
        target_fs = (int(input("Audio rate [32000]: ") or 32000))

        print("Making sound...")
        data = data - np.mean(data)
        data_n = data / np.amax(np.absolute(data))

        filename = "%s_%s.wav" % (filename.strip('.mseed'), target_fs)
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "wav", filename))
        print(path)

        librosa.output.write_wav(path, data_n, target_fs, norm=True)

        print("--> done")

        subprocess.check_call("open %s" % path, shell=True)



'''

save a file for the most recent chosen

select sensor channel from station

save plots and open in background

'''

