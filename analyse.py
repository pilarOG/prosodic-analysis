# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from configuration import load_config
from data_load import load_wave
from utils import extract_pitch, extract_intensity, extract_mfccs, extract_intervals, extract_harmonics, draw_pitch, draw_intens, draw_harmonic, draw_zcoef, plot_stats
import numpy as np
import os
import pysptk
from scipy.io import wavfile
import matplotlib.pyplot as plt
#np.set_printoptions(threshold=np.inf)

#TODO: what would be the point of accumulating mean, min and max? think about how to show it
perc_voiced, pitch_values, silence_values, harmonic_values = [], [], [], [] # Only leave those we'll use for stats
intens_values, zcoef_values, duration_values = [], [], []

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
        draw_pitch(self.pitch_countour, pitch_analysis.xs(), settings, 'original', filepath)
        # Interpolated contour
        self.interpolated = pitch_analysis.interpolate().selected_array['frequency']
        self.interpolated[self.interpolated==0] = np.nan
        draw_pitch(self.interpolated, pitch_analysis.xs(), settings, 'interpolated', filepath)
        # Smoothed version
        self.smoothed = pitch_analysis.smooth(bandwidth=self.settings.smooth_bandwidth).selected_array['frequency']
        self.smoothed[self.smoothed==0] = np.nan
        draw_pitch(self.smoothed, pitch_analysis.xs(), settings, 'smoothed', filepath)
        # Percentage of voiced frames # TODO: how to plot this?
        self.perc_voiced = (pitch_analysis.count_voiced_frames() * 100) / pitch_analysis.get_number_of_frames()
        perc_voiced.append(self.perc_voiced)

    # 2) Intensity: mean, range, contour, mean c0 coefficient
    def set_intensity_analysis(self, intensity_analysis, zero_coefs_analysis):
        self.intensity_analysis = intensity_analysis
        # Intensity countour
        self.intens_countour = [n[0] for n in intensity_analysis.values.T]
        self.intens_countour[self.intens_countour==0] = np.nan
        intens_values.append(self.intens_countour)
        draw_intens(self.intens_countour, intensity_analysis.xs(), settings, filepath)
        # Zero coefficient
        self.zero_coefs_analysis = zero_coefs_analysis
        zcoef_values.append(self.zero_coefs_analysis)
        draw_zcoef(self.zero_coefs_analysis, len(self.zero_coefs_analysis), settings, filepath)

    # 3) Duration: values (without silences), pause duration, speech/silence ratio
    def set_duration_analysis(self, duration_analysis, silence_analysis):
        self.duration_analysis = duration_analysis
        self.silence_analysis = silence_analysis
        self.ratio_speech_silence = duration_analysis // silence_analysis
        duration_values.append(self.duration_analysis)
        silence_values.append(self.silence_analysis)

    #TODO: I would like to add here a model that can detect the center of a vowel to get an unsupervised speech rate

    # 4) Voice quality: HNR
    def set_harmonic_analysis(self, harmonic_analysis):
        self.harmonic_analysis = harmonic_analysis
        # HNR countour
        self.harmonic_countour = [n[0] for n in harmonic_analysis.values.T]
        self.harmonic_countour[self.harmonic_countour==0] = np.nan
        harmonic_values.append(self.harmonic_countour)
        draw_harmonic(self.harmonic_countour, harmonic_analysis.xs(), settings, filepath)

# Future extra options:
# 1) Include gender information
# 2) Include alignments
# 3) Include speaker labels
# 4) Include through time analysis


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

        if settings.analyse_int:
            analysis.set_intensity_analysis(extract_intensity(analysis.wav, settings), extract_mfccs(wavfile.read(settings.corpora+'/'+filepath), settings))

        if settings.analyse_dur:
            durations, silences = extract_intervals(analysis.wav)
            analysis.set_duration_analysis(durations, silences)

        if settings.analyse_voc:
            analysis.set_harmonic_analysis(extract_harmonics(analysis.wav))

# Plot corpus stats
plot_stats(list(np.concatenate(pitch_values)), 'Fundamental frequency (Hz)', settings)
plot_stats(list(np.concatenate(intens_values)), 'Intensity (dB)', settings) # Concatenate values of all samples
plot_stats(duration_values, 'Duration (s)', settings)
plot_stats(silence_values, 'Silence (s)', settings)
plot_stats(list(np.concatenate(harmonic_values)), 'HNR (dB)', settings)

#TODO: table of means and other stats
