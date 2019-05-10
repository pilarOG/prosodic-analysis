

import parselmouth

# Load corpora waveforms
def load_wave(filepath):
    return parselmouth.Sound(filepath)
