# Load one file or corpora waveforms
# Load gender and alignments if there are any
import parselmouth


def load_wave(filepath):
    return parselmouth.Sound(filepath)
