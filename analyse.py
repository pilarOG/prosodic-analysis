from argparse import ArgumentParser
from configuration import load_config
from data_load import load_wave
from freq_utils import extract_pitch, draw_pitch
import numpy as np
#np.set_printoptions(threshold=np.inf)

class ProsodicAnalysis():
    def __init__(self, waveform, settings):
        self.wav = waveform
        self.settings = settings

    # 1) F0: mean, range, standard deviation, contour, un/voiced frames
    def set_pitch_analysis(self, pitch_analysis):
        # Original Praat object, we will only take what we want
        self.pitch_analysis = pitch_analysis
        # Array with fundamental frequency values
        self.pitch_countour = pitch_analysis.selected_array['frequency']
        self.pitch_countour[self.pitch_countour==0] = np.nan
        # Get plot of the contour
        draw_pitch(self.pitch_countour, pitch_analysis.xs(), settings, 'original')
        # Interpolated contour
        self.interpolated = pitch_analysis.interpolate().selected_array['frequency']
        self.interpolated[self.interpolated==0] = np.nan
        draw_pitch(self.interpolated, pitch_analysis.xs(), settings, 'interpolated')
        # Pitch slope
        self.slope_pitch = pitch_analysis.get_mean_absolute_slope()
        # General stats
        self.mean_pitch = np.nanmean(self.pitch_countour)
        self.max_pitch = pitch_analysis.xmax
        self.min_pitch = pitch_analysis.xmin
        self.range = pitch_analysis.xrange
        self.std_pitch = np.nanstd(self.pitch_countour)
        # Percentage of voiced frames
        self.perc_voiced = (pitch_analysis.count_voiced_frames() * 100) / pitch_analysis.get_number_of_frames()


# Features to extract
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
    analysis = ProsodicAnalysis(wav, settings)

    if settings.analyse_f0:
        analysis.set_pitch_analysis(extract_pitch(analysis.wav, settings))

    print analysis.interpolated
