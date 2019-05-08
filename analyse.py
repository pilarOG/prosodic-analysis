# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from configuration import load_config
from data_load import load_wave
from utils import extract_pitch, extract_intensity, extract_mfccs, draw_pitch, draw_intens, draw_zcoef, plot_stats, get_stats
import numpy as np
import os
import pysptk
from scipy.io import wavfile
#np.set_printoptions(threshold=np.inf)

#TODO: what would be the point of accumulating mean, min and max? think about how to show it
mean_pitch, max_pitch, min_pitch, std_pitch, perc_voiced, pitch_values = [], [], [], [], [], [] # Only leave those we'll use for stats
intens_values, zcoef_values = [], []

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
        # General stats
        self.mean_pitch, self.min_pitch, self.max_pitch, self.std_pitch = get_stats(self.pitch_countour)

        # Interpolated contour
        self.interpolated = pitch_analysis.interpolate().selected_array['frequency']
        self.interpolated[self.interpolated==0] = np.nan
        draw_pitch(self.interpolated, pitch_analysis.xs(), settings, 'interpolated', filepath)
        # Smoothed version
        self.smoothed = pitch_analysis.smooth(bandwidth=self.settings.smooth_bandwidth).selected_array['frequency']
        self.smoothed[self.smoothed==0] = np.nan
        draw_pitch(self.smoothed, pitch_analysis.xs(), settings, 'smoothed', filepath)
        # Pitch slope TODO: conider also get_slope_without_octave_jumps
        self.slope_pitch = pitch_analysis.get_mean_absolute_slope()
        # Percentage of voiced frames
        self.perc_voiced = (pitch_analysis.count_voiced_frames() * 100) / pitch_analysis.get_number_of_frames()
        perc_voiced.append(self.perc_voiced)

    # 2) Intensity: mean, range, contour, mean c0 coefficient
    def set_intensity_analysis(self, intensity_analysis, zero_coefs_analysis):
        self.intensity_analysis = intensity_analysis
        # Intensity countour
        self.intens_countour = intensity_analysis.values.T
        self.intens_countour[self.intens_countour==0] = np.nan
        intens_values.append(self.intens_countour)
        # General stats #TODO: add the general stats to each plot
        self.mean_intens, self.min_intens, self.max_intens, self.std_intens = get_stats(self.intens_countour)
        # Plot intensity
        draw_intens(self.intens_countour, intensity_analysis.xs(), settings, filepath)
        # Zero coefficient
        self.zero_coefs_analysis = zero_coefs_analysis
        zcoef_values.append(self.zero_coefs_analysis)
        # General stats
        self.mean_zcoef, self.min_zcoef, self.max_zcoef, self.std_zcoef = get_stats(self.zero_coefs_analysis)
        # Plot coefficient
        draw_zcoef(self.zero_coefs_analysis, len(self.zero_coefs_analysis), settings, filepath)

# Features to extract

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
    if '.wav' in filepath:
        wav = load_wave(settings.corpora+'/'+filepath)
        analysis = ProsodicAnalysis(wav, settings, filepath)

        if settings.analyse_f0: #TODO: give a choice about pitch tracker, or to use them all, compare them, and maybe tell the best one for that data
            analysis.set_pitch_analysis(extract_pitch(analysis.wav, settings))
            #print dir(analysis.pitch_analysis)

        if settings.analyse_int:
            analysis.set_intensity_analysis(extract_intensity(analysis.wav, settings), extract_mfccs(wavfile.read(settings.corpora+'/'+filepath), settings))
            #print dir(analysis.intensity_analysis)

# Plot corpus stats
# plot_stats([(list(np.concatenate(pitch_values)), 'pitch values')], settings)
# plot_stats([(list(np.concatenate(intens_values)), 'pitch values')], settings)
