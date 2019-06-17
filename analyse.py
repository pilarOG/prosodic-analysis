# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from configuration import load_config
from data_load import load_wave
from utils import extract_pitch, extract_intensity, extract_mfccs, extract_intervals, extract_harmonics, draw_pitch, draw_intens, draw_harmonic, draw_zcoef, plot_stats, plot_over_time
import numpy as np
import os
import pysptk
from scipy.io import wavfile
import matplotlib.pyplot as plt
from tqdm import tqdm

#TODO: what would be the point of accumulating mean, min and max? think about how to show it
perc_voiced, pitch_values, silence_values, harmonic_values = [], [], [], [] # Only leave those we'll use for stats
intens_values, zcoef_values, duration_values = [], [], []

speakers, genders, orders = [], [], []

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
        # Interpolated contour
        self.interpolated = pitch_analysis.interpolate().selected_array['frequency']
        self.interpolated[self.interpolated==0] = np.nan
        # Smoothed version
        self.smoothed = pitch_analysis.smooth(bandwidth=self.settings.smooth_bandwidth).selected_array['frequency']
        self.smoothed[self.smoothed==0] = np.nan
        draw_pitch(self.pitch_countour, self.smoothed, self.interpolated, pitch_analysis.xs(), settings, filepath)
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


#### MAIN ####

a = ArgumentParser()
a.add_argument('-c', dest='config', required=True, type=str)
opts = a.parse_args()
settings = load_config(opts.config)

# Analysis of each sample
for filepath in tqdm(sorted(os.listdir(settings.corpora))):
    if '.wav' in filepath:
        wav = load_wave(settings.corpora+'/'+filepath)
        analysis = ProsodicAnalysis(wav, settings, filepath)

        if settings.order_labels:
            orders.append(int(filepath.replace('.wav', '').split(settings.separator)[settings.order_labels-1]))

        if settings.speaker_labels:
            [speakers.append(label) for label in settings.speaker_labels if filepath.startswith(label)]

        if settings.gender_labels and settings.speaker_labels:
            [genders.append(settings.gender_labels[n]) for n in range(0, len(settings.speaker_labels)) if filepath.startswith(settings.speaker_labels[n])]

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


if settings.order_labels:
    if settings.analyse_f0: plot_over_time(orders, pitch_values, 'Fundamental frequency (Hz)', settings)
    if settings.analyse_int: plot_over_time(orders, intens_values, 'Intensity (dB)', settings)
    if settings.analyse_dur: plot_over_time(orders, duration_values, 'Duration (s)', settings)
    if settings.analyse_dur: plot_over_time(orders, silence_values, 'Silence (s)', settings)
    if settings.analyse_voc: plot_over_time(orders, harmonic_values, 'HNR (dB)', settings)

 # If we are simply plotting for the whole corpus

elif settings.speaker_labels == []:
    if settings.analyse_f0: plot_stats(list(np.concatenate(pitch_values)), 'Fundamental frequency (Hz)', settings)
    if settings.analyse_int: plot_stats(list(np.concatenate(intens_values)), 'Intensity (dB)', settings) # Concatenate values of all samples
    if settings.analyse_dur: plot_stats(duration_values, 'Duration (s)', settings)
    if settings.analyse_dur: plot_stats(silence_values, 'Silence (s)', settings)
    if settings.analyse_voc: plot_stats(list(np.concatenate(harmonic_values)), 'HNR (dB)', settings)
else:
# If we are plotting by speaker
    for speak in set(speakers):
        speaker_f0_values, speaker_int_values, speaker_dur_values, speaker_sil_values, speaker_har_values = [], [], [], [], []
        for n in range(0, len(speakers)):
            if speakers[n] == speak:
                if settings.analyse_f0: speaker_f0_values.append(pitch_values[n])
                if settings.analyse_int: speaker_int_values.append(intens_values[n])
                if settings.analyse_dur: speaker_dur_values.append(duration_values[n])
                if settings.analyse_dur: speaker_sil_values.append(silence_values[n])
                if settings.analyse_voc: speaker_har_values.append(harmonic_values[n])
        if settings.analyse_f0: plot_stats(list(np.concatenate(speaker_f0_values)), 'Fundamental frequency (Hz)', settings, speak)
        if settings.analyse_int: plot_stats(list(np.concatenate(speaker_int_values)), 'Intensity (dB)', settings, speak) # Concatenate values of all samples
        if settings.analyse_dur: plot_stats(speaker_dur_values, 'Duration (s)', settings, speak)
        if settings.analyse_dur: plot_stats(speaker_sil_values, 'Silence (s)', settings, speak)
        if settings.analyse_voc: plot_stats(list(np.concatenate(speaker_har_values)), 'HNR (dB)', settings, speak)

# If we are plotting by gender
if settings.speaker_labels and settings.gender_labels:
    for gen in set(genders):
        gender_f0_values, gender_int_values, gender_dur_values, gender_sil_values, gender_har_values = [], [], [], [], []
        for n in range(0, len(genders)):
            if genders[n] == gen:
                if settings.analyse_f0: gender_f0_values.append(pitch_values[n])
                if settings.analyse_int: gender_int_values.append(intens_values[n])
                if settings.analyse_dur: gender_dur_values.append(duration_values[n])
                if settings.analyse_dur: gender_sil_values.append(silence_values[n])
                if settings.analyse_voc: gender_har_values.append(harmonic_values[n])
        if settings.analyse_f0: plot_stats(list(np.concatenate(gender_f0_values)), 'Fundamental frequency (Hz)', settings, gen)
        if settings.analyse_int: plot_stats(list(np.concatenate(gender_int_values)), 'Intensity (dB)', settings, gen) # Concatenate values of all samples
        if settings.analyse_dur: plot_stats(gender_dur_values, 'Duration (s)', settings, gen)
        if settings.analyse_dur: plot_stats(gender_sil_values, 'Silence (s)', settings, gen)
        if settings.analyse_voc: plot_stats(list(np.concatenate(gender_har_values)), 'HNR (dB)', settings, gen)



#TODO: extra information
# Future extra options:
# 2) Include vowel detection model
# 4) Include through time analysis
