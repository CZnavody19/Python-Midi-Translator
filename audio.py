import soundcard as sc
import numpy

default_speaker = sc.default_speaker()
default_mic = sc.default_microphone()

data = default_mic.record(samplerate=48000, numframes=48000)
default_speaker.play(data/numpy.max(data), samplerate=48000)

with default_mic.recorder(samplerate=48000, blocksize=1024) as mic, \
      default_speaker.player(samplerate=48000) as sp:
    while True:
        data = mic.record(numframes=1024)
        sp.play(data)