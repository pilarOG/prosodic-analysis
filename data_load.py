# Load one file or corpora waveforms
# Load gender and alignments if there are any
import parselmouth


def load_wave(path):
    return parselmouth.Sound(path)
