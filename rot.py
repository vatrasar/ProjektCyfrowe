from scipy.io import wavfile
import pyqtgraph as pg
from scipy.io import wavfile
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from scipy.fftpack import fft,fftfreq
import matplotlib.pyplot as plt
rate, audio = wavfile.read("dzwieki/bzyk.wav")

audio = np.mean(audio, axis=1)
N = audio.shape[0]
L = N / rate

print(f'Audio length: {L:.2f} seconds')

f, ax = plt.subplots()
ax.plot(np.arange(N) / rate, audio)
ax.set_xlabel('Time [s]')
ax.set_ylabel('Amplitude [unknown]')
from skimage import util

M = 1024

# slices = util.view_as_windows(audio, window_shape=(M,), step=100)
# win = np.hanning(M + 1)[:-1]
# slices = slices * win
# slices = slices.T
spectrum = np.fft.fft(audio, axis=0)[:M // 2 + 1:-1]
spectrum = np.abs(spectrum)
f, ax = plt.subplots(figsize=(4.8, 2.4))

S = np.abs(spectrum)
S = 20 * np.log10(S / np.max(S))

ax.imshow(S, origin='lower', cmap='viridis',
          extent=(0, L, 0, rate / 2 / 1000))
ax.axis('tight')
ax.set_ylabel('Frequency [kHz]')
ax.set_xlabel('Time [s]');