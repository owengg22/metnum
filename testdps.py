import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import firwin, lfilter, freqz

# 1. LOAD DATA
df = pd.read_csv('dataset.txt', sep=';', decimal=',', header=None, names=['Time', 'Amplitude'])
signal = df['Amplitude'].values
time = df['Time'].values

# 2. PARAMETER BANDPASS UNTUK QRS
fs = 500.0       # Sampling rate (tetap 500 Hz)

# KUNCI UTAMA DI SINI:
f_low = 8.0      # Cutoff Bawah (Buang T-wave 7 Hz)
f_high = 20.0    # Cutoff Atas (Buang Noise Otot)

M = 50           # Order Filter
numtaps = 2*M + 1

# 3. DESAIN FILTER (BANDPASS)
# pass_zero=False -> Bandpass (DC/0Hz dibuang)
coefficients = firwin(numtaps, cutoff=[f_low, f_high], fs=fs, window='hamming', pass_zero=False)

# 4. FILTERING
filtered_signal = lfilter(coefficients, 1.0, signal)

# Koreksi Delay (Agar grafik pas tumpuk)
delay = int(0.5 * (numtaps - 1))
filtered_signal_corrected = np.roll(filtered_signal, -delay)

# 5. PLOTTING
plt.figure(figsize=(12, 8))

# Plot Sinyal
plt.subplot(2, 1, 1)
plt.plot(time, signal, label='Original ECG (Raw)', color='lightgray', alpha=0.8)
plt.plot(time, filtered_signal_corrected, label=f'QRS Detection (Bandpass {f_low}-{f_high} Hz)', color='green', linewidth=2)
plt.title(f'Deteksi QRS Complex (Membuang T-Wave dan P-Wave)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.xlim(0, 5) # Zoom 5 detik pertama

# Plot Respon Frekuensi
plt.subplot(2, 1, 2)
w, h = freqz(coefficients, worN=8000)
freq_xaxis = (w * fs) / (2 * np.pi)
plt.plot(freq_xaxis, 20 * np.log10(abs(h)), color='green')
plt.title('Frequency Response of QRS Filter')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Gain (dB)')
plt.axvline(7, color='orange', linestyle=':', label='T-Wave (7 Hz) - Diredam')
plt.axvline(10, color='red', linestyle='--', label='QRS (10 Hz) - Diloloskan')
plt.axvline(f_low, color='black', linestyle='-', label='Cutoff')
plt.axvline(f_high, color='black', linestyle='-')
plt.xlim(0, 50)
plt.ylim(-60, 5)
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()