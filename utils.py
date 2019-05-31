# -*- coding: utf-8 -*-

# Functions for fundamental frequency analysis
import numpy as np
import parselmouth
import matplotlib.pyplot as plt
import pysptk
import matplotlib.mlab as mlab
plt.style.use('ggplot')

# TODO: extract features as a different step to not repeat?

def extract_pitch(waveform, settings):
    return waveform.to_pitch(pitch_ceiling=settings.pitch_ceiling, pitch_floor=settings.pitch_floor)

def extract_intensity(waveform, settings):
    return waveform.to_intensity()

def extract_mfccs(waveform, settings):
    zero_coefs = []
    fs = waveform[0]
    x = waveform[1]
    if len(x.shape) > 1 and x.shape[1] == 2:
        x = x[:, 0]
    for pos in range(0, len(x)-settings.frame_length, settings.frame_length):
        xw = x[pos:pos+settings.frame_length] * pysptk.blackman(settings.frame_length)
        zero_coefs.append(pysptk.sptk.mfcc(xw, fs=fs, order=14, czero=True)[-1])
    return zero_coefs

def extract_intervals(waveform):
    text_grid = parselmouth.praat.call(waveform, "To TextGrid (silences)", 100, 0.0, -25.0, 0.1, 0.1, 'silent', 'sounding')
    soundings = parselmouth.praat.call([text_grid, waveform], "Extract intervals where", 1, False, 'is equal to','sounding')
    silences = parselmouth.praat.call([text_grid, waveform], "Extract intervals where", 1, False, 'is equal to','silent')
    if type(soundings) == list:
        duration = sum([sound.duration for sound in soundings])
    else: #If only one interval found
        duration = soundings.duration
    if type(silences) == list:
        pauses = sum([silence.duration for silence in silences])
    else:
        pauses = silences.duration
    return duration, pauses

def extract_harmonics(waveform):
    return parselmouth.praat.call(waveform, "To Harmonicity (cc)", 0.01, 75.0, 0.1, 4.5)

#TODO: pick different colours for the different graphs

# From original https://github.com/YannickJadoul/Parselmouth
def draw_pitch(pitch, smoothed, interpolated, xaxis, settings, filepath):
    plt.clf()
    plt.ylim(settings.pitch_floor, settings.pitch_ceiling)
    plt.ylabel("Fundamental Frequency (Hz)")
    plt.xlabel("Time (s)")
    plt.plot(xaxis, pitch, color='red', label='pitch')
    plt.plot(xaxis, interpolated, color='purple', label='interpolated', alpha=0.5)
    plt.plot(xaxis, smoothed, color='blue', label='smoothed')
    plt.legend()
    plt.title('Pitch '+filepath.replace('.wav', ''))
    plt.savefig(settings.save_plots+'/f0_'+filepath.replace('wav', 'png'))

def draw_intens(intens_values, xaxis, settings, filepath):
    plt.clf()
    plt.ylim(0, 120)
    plt.ylabel("Intensity (dB)")
    plt.xlabel("Time (s)")
    plt.plot(xaxis, intens_values, color='red')
    plt.title('Intensity '+filepath.replace('.wav', ''))
    plt.savefig(settings.save_plots+'/intens_'+filepath.replace('wav', 'png'))

def draw_zcoef(coef_values, xaxis_len, settings, filepath):
    plt.clf()
    plt.ylim(0, 70)
    plt.ylabel("Zero Coefficient")
    plt.xlabel("Frames")
    plt.plot(range(0, xaxis_len), coef_values, color='orange')
    plt.title('Power '+filepath.replace('.wav', ''))
    plt.savefig(settings.save_plots+'/zcoef_'+filepath.replace('wav', 'png'))

def draw_harmonic(harmonic_values, xaxis, settings, filepath):
    plt.clf()
    plt.ylim(0, 25)
    plt.ylabel("Intensity (dB)")
    plt.xlabel("Time (s)")
    plt.plot(xaxis, harmonic_values, color='pink')
    plt.title('HNR '+filepath.replace('.wav', ''))
    plt.savefig(settings.save_plots+'/harmonic_'+filepath.replace('wav', 'png'))

def plot_stats(indicator, name, settings, speaker=None, bins=25):
    plt.clf()
    values = [x for x in indicator if ~np.isnan(x)]
    # Plot histogram
    minv = min(values)
    if minv < 0: minv = 0
    plt.xlim(minv, max(values))
    n, bins, _ = plt.hist(values, bins='auto', normed=1, color='blue')
    plt.ylim(0, max(n))
    if speaker: plt.title(settings.title+' '+speaker)
    else: plt.title(settings.title)
    # Mean line
    values = [x for x in indicator if x > 0]
    plt.axvline(np.nanmean(values), color='k', linestyle='dashed', linewidth=1)
    plt.ylabel('Normalized frequency')
    plt.xlabel(name.split()[0])
    # Distribution fit
    y = mlab.normpdf(bins, np.nanmean(values), np.nanstd(values))
    plt.plot(bins, y, 'r--')
    # Save plot
    if speaker: plt.savefig(settings.save_plots+'/'+settings.title+'_'+speaker+'_stats_'+name.split()[0]+'.png')
    else: plt.savefig(settings.save_plots+'/'+settings.title+'_stats_'+name.split()[0]+'.png')
