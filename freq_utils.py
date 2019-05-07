# Functions for fundamental frequency analysis
import numpy as np
import parselmouth
import matplotlib.pyplot as plt

def extract_pitch(waveform, settings):
    return waveform.to_pitch(pitch_ceiling=settings.pitch_ceiling, pitch_floor=settings.pitch_floor)

# From original https://github.com/YannickJadoul/Parselmouth
def draw_pitch(pitch_values, xaxis, settings, mode):
    plt.clf()
    plt.plot(xaxis, pitch_values)
    plt.ylim(0, settings.pitch_ceiling)
    plt.ylabel("fundamental frequency [Hz]")
    plt.savefig(settings.save_plots+'/'+mode+'_'+settings.stats_sample.replace('wav', 'png'))
