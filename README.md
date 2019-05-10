# Prosodic Analysis

Tool to analyze general prosodic features of an audio speech corpora (in any language) in terms of intonation, intensity, duration and voice quality. 
This can be a useful tool for anyone working with speech datasets, and can help as a first general analysis of the prosodic characteristics of a dataset.

## Installation

The scripts rely in two main libraries: parselmouth (a Python wrapper of Praat: https://github.com/YannickJadoul/Parselmouth) and pysptk (a Python wrapper of the Speech ToolKit: https://pysptk.readthedocs.io/en/latest/index.html). Most of the analysis are done with the Praat wrapper, because although is slower than sptk, most phoneticians use it and in my experience is a very reliable tool.

Clone the repository and install the required dependencies with:

```bash
pip install -r requirements.txt
```


## Usage

To use the script you only need to modify the config.cfg file. This file contains the path to the audio corpora and the parameters to make the analysis.

```bash
python analyse.py -c config.cfg
```

# Output

The script runs 4 kinds of analysis (which can be turned on or off in the config file): pitch, duration (of speech and pauses seprately), intensity and harmonic-to-noise ratio.
Analysis are run both for each sentence and for the whole corpora.

One of the datasets I will use here to examplify is the LJ dataset that you can find here: https://keithito.com/LJ-Speech-Dataset/

For each sentence, the outputs are:
- Fundamental frequency contour (in Hz) of pitch, interpolated and smoothed contour plot for each sentence.
- Intensity contour (in dB) plots for each sentence.
- Zero coefficient plots for each sentence.
- HNR (in dB) plots for each sentence.

This is an example of the mentioned plots for one sentence in the LJ dataset.
![Alt text](plots/f0_LJ050-0008.png?raw=true)

For the corpora, the outputs are:
- Normalized histogram of the distribution of fundamental frequency (in Hz) values.
- Normalized histogram of the distribution of intensity (in dB) values.
- Normalized histogram of the distribution of duration of speech segments (in seconds) values.
- Normalized histogram of the distribution of duration of silence segments (in seconds) values.
- Normalized histogram of the distribution of HNR (in dB) values.


