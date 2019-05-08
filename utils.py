# -*- coding: utf-8 -*-

# Functions for fundamental frequency analysis
import numpy as np
import parselmouth
import matplotlib.pyplot as plt
import seaborn as sns
import pysptk

def extract_pitch(waveform, settings):
    return waveform.to_pitch(pitch_ceiling=settings.pitch_ceiling, pitch_floor=settings.pitch_floor)

def extract_intensity(waveform, settings):
    return waveform.to_intensity()

def extract_mfccs(waveform, settings):
    zero_coefs = []
    fs = waveform[0]
    x = waveform[1]
    for pos in range(0, len(x)-settings.frame_length, settings.frame_length):
        xw = x[pos:pos+settings.frame_length] * pysptk.blackman(settings.frame_length)
        zero_coefs.append(pysptk.sptk.mfcc(xw, fs=fs, order=14, czero=True)[-1])
    return zero_coefs

# From original https://github.com/YannickJadoul/Parselmouth
def draw_pitch(pitch_values, xaxis, settings, mode, filepath):
    plt.clf()
    plt.ylim(0, settings.pitch_ceiling)
    plt.ylabel("fundamental frequency [Hz]")
    plt.plot(xaxis, pitch_values)
    plt.savefig(settings.save_plots+'/f0_'+mode+'_'+filepath.replace('wav', 'png'))

def draw_intens(intens_values, xaxis, settings, filepath):
    plt.clf()
    plt.ylim(0, 120)
    plt.ylabel("intensity [dB]")
    plt.plot(xaxis, intens_values)
    plt.savefig(settings.save_plots+'/intens_'+filepath.replace('wav', 'png'))

def draw_zcoef(coef_values, xaxis_len, settings, filepath):
    plt.clf()
    plt.ylim(0, 70)
    plt.ylabel("zero coefficient")
    plt.xlabel("windows")
    plt.plot(range(0, xaxis_len), coef_values)
    plt.savefig(settings.save_plots+'/zcoef_'+filepath.replace('wav', 'png'))

def get_stats(values):
    values[values==0] = np.nan
    return np.nanmean(values), np.nanmin(values), np.nanmax(values), np.nanstd(values)


def plot_stats(indicators, settings):
    for indicator in indicators:
        plt.clf()
        values = [x for x in indicator[0] if ~np.isnan(x)]
        name = indicator[1]
        plt.xlim(min(values), max(values))
        plt.ylim(0, len(values)/2)
        plt.hist(values, bins=25)
        plt.xlabel(name)
        plt.show()
