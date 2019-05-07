# Functions for fundamental frequency analysis

import parselmouth

def extract_pitch(waveform):
    return waveform.to_pitch()
