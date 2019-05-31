

import parselmouth

# Load corpora waveforms
def load_wave(filepath): # TODO: convert to mono
    waveform = parselmouth.Sound(filepath)
    waveform = parselmouth.praat.call(waveform, "Convert to mono")
    return waveform
