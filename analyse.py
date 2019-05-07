from argparse import ArgumentParser
from configuration import load_config
from data_load import load_wave
from freq_utils import extract_pitch
import numpy as np
#np.set_printoptions(threshold=np.inf)

class ProsodicAnalysis():
    def __init__(self, waveform):
        self.wav = waveform

    def set_pitch_analysis(self, pitch_analysis):

        self.pitch_analysis = pitch_analysis

        # Array with fundamental frequency values
        self.pitch_countour = pitch_analysis.selected_array['frequency']
        self.pitch_countour[self.pitch_countour==0] = np.nan

        # Maximum value used to extract pitch values
        self.ceiling = pitch_analysis.ceiling


        self.mean_absolute_slope = pitch_analysis.get_mean_absolute_slope()

        self.max_pitch = pitch_analysis.xmax

        self.min_pitch = pitch_analysis.xmin

        self.range = pitch_analysis.xrange


    #def get_pitch_analysis(self):
    #    return self.pitch_analysis

# Features to extract
# 1) F0: mean, range, standard deviation, contour, un/voiced frames
# 2) Intensity: mean, range, standard deviation, contour, mean c0 coefficient
# 3) Duration: range, mean (without silences), standard deviation
# 4) Speech rate: units per second
# 5) Vocal quality: HNR, glottal source open quotient
# 6) Pause: mean duration, range duration, pauses per second, ratio of pauses/speech


# Two modes:
# 1) Collect statistics per sample
# 2) or collect statistics for a full corpus


# Two extra options:
# 1) Include gender information
# 2) Include alignments

#### Load configuration options

a = ArgumentParser()
a.add_argument('-c', dest='config', required=True, type=str)
opts = a.parse_args()
settings = load_config(opts.config)

if settings.stats_sample:
    wav = load_wave(settings.stats_sample)
    analysis = ProsodicAnalysis(wav)

    if settings.analyse_f0:
        analysis.set_pitch_analysis(extract_pitch(analysis.wav))

    print analysis.ceiling
