# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from configuration import load_config
from data_load import load_wave
from utils import extract_pitch, draw_pitch, plot_pitch_stats
import numpy as np
import os
#np.set_printoptions(threshold=np.inf)

mean_pitch, max_pitch, min_pitch, range_pitch, std_pitch, perc_voiced, pitch_values = [], [], [], [], [], [], []

class ProsodicAnalysis():

    def __init__(self, waveform, settings, filepath):
        self.wav = waveform
        self.settings = settings
        self.filepath = filepath

    # 1) F0: mean, range, standard deviation, contour, un/voiced frames
    def set_pitch_analysis(self, pitch_analysis):
        # Original Praat object, we will only take what we want
        self.pitch_analysis = pitch_analysis
        # Array with fundamental frequency values
        self.pitch_countour = pitch_analysis.selected_array['frequency']
        self.pitch_countour[self.pitch_countour==0] = np.nan
        pitch_values.append(self.pitch_countour)
        # Get plot of the contour
        draw_pitch(self.pitch_countour, pitch_analysis.xs(), settings, 'original', filepath)
        # Interpolated contour
        self.interpolated = pitch_analysis.interpolate().selected_array['frequency']
        self.interpolated[self.interpolated==0] = np.nan
        draw_pitch(self.interpolated, pitch_analysis.xs(), settings, 'interpolated', filepath)
        # TODO: add a smoothed version
        self.smoothed = pitch_analysis.smooth(bandwidth=self.settings.smooth_bandwidth).selected_array['frequency']
        self.smoothed[self.smoothed==0] = np.nan
        draw_pitch(self.smoothed, pitch_analysis.xs(), settings, 'smoothed', filepath)
        # Pitch slope TODO: conider also get_slope_without_octave_jumps
        self.slope_pitch = pitch_analysis.get_mean_absolute_slope()
        # General stats
        self.mean_pitch = np.nanmean(self.pitch_countour)
        mean_pitch.append(self.mean_pitch)
        self.max_pitch = np.nanmax(self.pitch_countour)
        max_pitch.append(self.max_pitch)
        self.min_pitch = np.nanmin(self.pitch_countour)
        min_pitch.append(self.min_pitch)
        self.range_pitch = pitch_analysis.xrange
        range_pitch.append(self.range_pitch)
        self.std_pitch = np.nanstd(self.pitch_countour)
        std_pitch.append(self.std_pitch)
        # Percentage of voiced frames
        self.perc_voiced = (pitch_analysis.count_voiced_frames() * 100) / pitch_analysis.get_number_of_frames()
        perc_voiced.append(self.perc_voiced)


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

#### MAIN ####

a = ArgumentParser()
a.add_argument('-c', dest='config', required=True, type=str)
opts = a.parse_args()
settings = load_config(opts.config)

# Analysis of each sample
for filepath in os.listdir(settings.corpora):
    wav = load_wave(settings.corpora+'/'+filepath)
    analysis = ProsodicAnalysis(wav, settings, filepath)

    if settings.analyse_f0:
        analysis.set_pitch_analysis(extract_pitch(analysis.wav, settings))
        #print dir(analysis.pitch_analysis)

# Plot corpus stats
plot_pitch_stats([(list(np.concatenate(pitch_values)), 'pitch values'), (perc_voiced, 'perc_voiced')], settings)
