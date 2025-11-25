import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


data = pd.read_csv("ecg.csv", header=None)

x = data.iloc[:, 0].values
y = data.iloc[:, 1].values

signal_length = np.sqrt(x**2 + y**2)
t = np.arange(len(signal_length))

order = 5   

coeffs = np.polyfit(t, y, order)        
baseline = np.polyval(coeffs, t)      
y_detrended = y - baseline


Sr = np.sum((y - baseline) ** 2)        
St = np.sum((y - np.mean(y)) ** 2)     
r2 =  1 - Sr / St

print("Order polynomial =", order)
print("Koefisien regresi =", coeffs)
print("Nilai r^2 =", r2)


plt.figure(figsize=(14, 5))
plt.plot(t, y, label='Sinyal ECG asli')
plt.plot(t, baseline, label='Baseline (Polynomial)', linewidth=2)
plt.title(f"Sinyal ECG & Baseline (Order {order}) - r² = {r2:.4f}")
plt.legend()
plt.grid()
plt.show()

plt.figure(figsize=(14, 5))
plt.plot(t, y_detrended, label='Sinyal setelah koreksi baseline')
plt.title("Sinyal FECG Detrended")
plt.legend()
plt.grid()
plt.show()
